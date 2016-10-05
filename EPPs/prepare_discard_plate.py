import argparse
from logging import FileHandler
import sys
from genologics.entities import Process
from genologics.lims import Lims
from egcg_core.app_logging import logging_default as log_cfg

if sys.version_info.major == 2:
    import urlparse
else:
    from urllib import parse as urlparse


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


def get_workflow_stage(lims, workflow_name, stage_name=None):
    workflows = [w for w in lims.get_workflows() if w.name == workflow_name]
    if len(workflows) != 1:
        return
    if not stage_name:
        return workflows[0].stages[0]
    stages = [s for s in workflows[0].stages if s.name == stage_name]
    if len(stages) != 1:
        return
    return stages[0]


def find_plate_to_route(lims, step_id):
    # Find the Discard plate workflow uri
    discard_plate_stage = get_workflow_stage(lims, workflow_name=discard_wf_name, stage_name=plate_discard_wf_stage_name)
    logger.info('Found Stage %s uri: %s', plate_discard_wf_stage_name, discard_plate_stage.uri)
    # Get the process currently running
    p = Process(lims, id=step_id)

    # Fetch the artifacts associated with the step
    step_artifacts = p.all_inputs()
    lims.get_batch(step_artifacts)

    # Fetch the sample associated with these artifacts
    samples = [a.samples[0] for a in step_artifacts]
    lims.get_batch(samples)
    logger.info('Found %d Samples in the step', len(samples))
    # Fetch the all the artifacts associated with these samples
    step_associated_artifacts = fetch_all_artifacts_for_samples(lims, samples)
    logger.info('Found %d Analytes (derived samples)', len(step_associated_artifacts))
    # List all the containers and retrive them
    containers = list(set([a.container for a in step_associated_artifacts]))
    batch_limit(lims, containers)
    logger.info('Found %d containers', len(containers))

    # Filter the containers to keep the one that are valid
    valid_containers = [c for c in containers if is_valid_container(c)]
    logger.info('Found %d valid containers to potentially discard', len(valid_containers))

    # Get all the artifacts in the valid containers and retrieve the one that were not retrieved already
    container_artifacts = set()
    for c in valid_containers:
        container_artifacts.update(set(c.placements.values()))

    non_step_atifacts = container_artifacts.difference(set(step_associated_artifacts))
    batch_limit(lims, list(non_step_atifacts))
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
    lims.route_artifacts(artifacts_to_route, stage_uri=discard_plate_stage.uri)

    # TODO: clean up steps where the step_associated_artifacts are queued


def main():
    args = _parse_args()
    r1 = urlparse.urlsplit(args.step_uri)
    server_http = '%s://%s' % (r1.scheme, r1.netloc)

    # Assume the step_uri contains the step id at the end
    step_id = r1.path.split('/')[-1]
    lims = Lims(server_http, args.username, args.password)

    log_cfg.add_handler(FileHandler(args.log_file))
    return find_plate_to_route(lims, step_id)


def _parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--username', dest='username', type=str, required=True, help='The username of the person logged in')
    p.add_argument('--password', dest='password', type=str, required=True, help='The password used by the person logged in')
    p.add_argument('--step_uri', dest='step_uri', type=str, required=True, help='The uri of the step this EPP is attached to')
    p.add_argument('--log_file', dest='log_file', type=str, required=True, help='The log file containing statement about what was done')
    return p.parse_args()


if __name__ == '__main__':
    sys.exit(main())
