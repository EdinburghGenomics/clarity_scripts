import sys
from logging import FileHandler
from egcg_core.app_logging import logging_default as log_cfg
from EPPs.common import EPP, argparser, get_workflow_stage

invalid_suffixes = {'-QNT', '-CFP', '-NRM', '-IMP', '-SSI', '-ALP', '-CAP', '-PCR', '-CPP', '-LQC', '-DQC1',
                    '-DIL1', '-DIL2', '-QPCR', '-CST'}

discard_wf_name = 'Discard Plates EG 1.0'
sample_discard_wf_stage_name = 'Find Derived Sample Plates EG 1.0'
plate_discard_wf_stage_name = 'Discard Plates EG 1.0'


logger = log_cfg.get_logger(__name__)


def batch_limit(lims, list_instance, max_query=100):
    for start in range(0, len(list_instance), max_query):
        lims.get_batch(list_instance[start:start+max_query])


def fetch_all_artifacts_for_samples(lims, samples):
    """
    search for all the artifact associated with a list of samples.
    To avoid too long a query we limit to 50 samples per query
    """
    lims_ids = [s.id for s in samples]
    max_query = 50
    artifacts = []
    for start in range(0, len(lims_ids), max_query):
        artifacts.extend(lims.get_artifacts(samplelimsid=lims_ids[start:start+max_query], type='Analyte'))
    batch_limit(lims, artifacts)
    return artifacts


def is_valid_container(container):
    for suffix in invalid_suffixes:
        if container.name.endswith(suffix):
            return False
    if container.type.name == 'Patterned Flowcell':
        return False
    return True


def has_workflow_stage(artifact, workflow_step_name):
    """
    Checks that the artifact's sample's root artifact has been through the given workflow.
    :return True if it has False otherwise
    """
    for w, status, name in artifact.samples[0].artifact.workflow_stages_and_statuses:
        if name == workflow_step_name and status == 'COMPLETE':
            return True
    return False


class FindPlateToRoute(EPP):
    def _run(self):
        # Find the Discard plate workflow uri
        discard_plate_stage = get_workflow_stage(self.lims, workflow_name=discard_wf_name, stage_name=plate_discard_wf_stage_name)
        logger.info('Found Stage %s uri: %s', plate_discard_wf_stage_name, discard_plate_stage.uri)

        # Fetch the artifacts associated with the step
        step_artifacts = self.process.all_inputs()
        self.lims.get_batch(step_artifacts)

        # Fetch the sample associated with these artifacts
        samples = [a.samples[0] for a in step_artifacts]
        self.lims.get_batch(samples)
        logger.info('Found %d Samples in the step', len(samples))
        # Fetch the all the artifacts associated with these samples
        step_associated_artifacts = fetch_all_artifacts_for_samples(self.lims, samples)
        logger.info('Found %d Analytes (derived samples)', len(step_associated_artifacts))
        # List all the containers and retrieve them
        containers = list(set([a.container for a in step_associated_artifacts]))
        batch_limit(self.lims, containers)
        logger.info('Found %d containers', len(containers))

        # Filter the containers to keep the one that are valid
        valid_containers = [c for c in containers if is_valid_container(c)]
        logger.info('Found %d valid containers to potentially discard', len(valid_containers))

        # Get all the artifacts in the valid containers and retrieve the one that were not retrieved already
        container_artifacts = set()
        for c in valid_containers:
            container_artifacts.update(set(c.placements.values()))

        non_step_atifacts = container_artifacts.difference(set(step_associated_artifacts))
        batch_limit(self.lims, list(non_step_atifacts))
        logger.info(
            'Found %d other to associated with the container but not associated with discarded samples',
            len(non_step_atifacts)
        )

        artifacts_to_route = []
        container_to_route = []
        for container in valid_containers:
            route_allowed = True
            logger.info(
                'Test container %s, with %s artifacts',
                container.name,
                len(container.placements.values())
            )
            for artifact in list(container.placements.values()):
                if artifact in step_associated_artifacts or has_workflow_stage(artifact, sample_discard_wf_stage_name):
                    logger.info(
                        'Container %s might route because artifact %s in step_associated_artifacts (%s) or has been discarded before (%s)',
                        container.name, artifact.name, artifact in step_associated_artifacts, has_workflow_stage(artifact, sample_discard_wf_stage_name)
                    )
                else:
                    # This container will have to wait
                    route_allowed = False
                    logger.info(
                        'Container: %s wont route because artifact %s in step_associated_artifacts (%s) or has been discard before (%s)',
                        container.name, artifact.name, artifact in step_associated_artifacts, has_workflow_stage(artifact, sample_discard_wf_stage_name)
                    )
            if route_allowed:
                artifacts_to_route.extend(list(container.placements.values()))
                container_to_route.append(container)
                logger.info('Will route container: %s', container.name)
        logger.info('Route %s containers with %s artifacts', len(container_to_route), len(artifacts_to_route))
        print('Route %s containers with %s artifacts', len(container_to_route), len(artifacts_to_route))
        self.lims.route_artifacts(artifacts_to_route, stage_uri=discard_plate_stage.uri)

        # TODO: clean up steps where the step_associated_artifacts are queued


def main():
    args = argparser().parse_args()
    log_cfg.add_handler(FileHandler(args.log_file))
    action = FindPlateToRoute(args.step_uri, args.username, args.password)
    return action.run()


if __name__ == '__main__':
    sys.exit(main())
