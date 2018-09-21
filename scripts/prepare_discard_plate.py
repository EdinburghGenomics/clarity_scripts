#!/usr/bin/env python
import re
import sys

from EPPs.common import StepEPP, get_workflow_stage

# valid name formats of the derived plates that should be located by the script (other derived plates are disposed of by date)

valid_names = {r'LP[0-9]{7}-GTY', r'LP[0-9]{7}-DNA', r'\w*P[0-9]{3}$'}

discard_wf_name = 'Sample Disposal EG 1.0 WF'
sample_discard_wf_stage_name = 'Request Sample Disposal EG 1.0 ST'
plate_discard_wf_stage_name = 'Dispose of Samples EG 1.0 ST'


def batch_limit(lims, list_instance, max_query=100):
    for start in range(0, len(list_instance), max_query):
        lims.get_batch(list_instance[start:start + max_query])


def fetch_all_artifacts_for_samples(lims, samples):
    """
    search for all the artifact associated with a list of samples.
    To avoid too long a query we limit to 50 samples per query
    """
    lims_ids = [s.id for s in samples]
    max_query = 50
    artifacts = []
    for start in range(0, len(lims_ids), max_query):
        artifacts.extend(lims.get_artifacts(samplelimsid=lims_ids[start:start + max_query], type='Analyte'))
    batch_limit(lims, artifacts)
    return artifacts


def is_valid_container(container):
    for name in valid_names:
        if re.match(name, container.name):
            return True
    return False


def has_workflow_stage(artifact, workflow_step_name):
    """
    Checks that the artifact's sample's root artifact has been through the given workflow.
    :return True if it has False otherwise
    """
    for w, status, name in artifact.samples[0].artifact.workflow_stages_and_statuses:
        if name == workflow_step_name and status == 'COMPLETE':
            return True
    return False


class FindPlateToRoute(StepEPP):
    _use_load_config = False
    def _run(self):

        # Find the Discard plate workflow uri
        discard_plate_stage = get_workflow_stage(self.lims, workflow_name=discard_wf_name,
                                                 stage_name=plate_discard_wf_stage_name)
        self.info('Found Stage %s uri: %s', plate_discard_wf_stage_name, discard_plate_stage.uri)

        # Fetch the artifacts associated with the step
        step_artifacts = self.process.all_inputs()
        self.lims.get_batch(step_artifacts)

        # Fetch the samples associated with these artifacts
        samples = [a.samples[0] for a in step_artifacts]
        self.lims.get_batch(samples)
        self.info('Found %d Samples in the step', len(samples))

        # Fetch the all the artifacts associated with these samples
        step_associated_artifacts = fetch_all_artifacts_for_samples(self.lims, samples)
        self.info('Found %d Analytes (derived samples)', len(step_associated_artifacts))

        # List all the containers and retrieve them
        containers = list(set(a.container for a in step_associated_artifacts))
        batch_limit(self.lims, containers)
        self.info('Found %d containers', len(containers))

        # Filter the containers to keep the one that are valid
        valid_containers = [c for c in containers if is_valid_container(c)]
        self.info('Found %d valid containers to potentially discard', len(valid_containers))

        # Get all the artifacts in the valid containers and retrieve the one that were not retrieved already
        container_artifacts = set()
        for c in valid_containers:
            container_artifacts.update(set(c.placements.values()))

        non_step_artifacts = container_artifacts.difference(set(step_associated_artifacts))
        batch_limit(self.lims, list(non_step_artifacts))
        self.info(
            'Found %d others associated with the container but not associated with discarded samples',
            len(non_step_artifacts)
        )

        artifacts_to_route = []
        container_to_route = []
        for container in valid_containers:
            route_allowed = True
            self.info(
                'Test container %s, with %s artifacts',
                container.name,
                len(container.placements.values())
            )
            for artifact in list(container.placements.values()):
                if artifact in step_associated_artifacts or has_workflow_stage(artifact, sample_discard_wf_stage_name):
                    self.info(
                        'Container %s might route because artifact %s in step_associated_artifacts (%s) or has been discarded before (%s)',
                        container.name, artifact.name, artifact in step_associated_artifacts,
                        has_workflow_stage(artifact, sample_discard_wf_stage_name)
                    )
                else:
                    # This container will have to wait
                    route_allowed = False
                    self.info(
                        "Container: %s won't route because artifact %s in step_associated_artifacts (%s) or has been discarded before (%s)",
                        container.name, artifact.name, artifact in step_associated_artifacts,
                        has_workflow_stage(artifact, sample_discard_wf_stage_name)
                    )
            if route_allowed:
                artifacts_to_route.extend(list(container.placements.values()))
                container_to_route.append(container)
                self.info('Will route container: %s', container.name)
        self.info('Route %s containers with %s artifacts', len(container_to_route), len(artifacts_to_route))
        self.lims.route_artifacts(artifacts_to_route, stage_uri=discard_plate_stage.uri)
        # TODO: clean up steps where the step_associated_artifacts are queued


if __name__ == '__main__':
    sys.exit(FindPlateToRoute().run())
