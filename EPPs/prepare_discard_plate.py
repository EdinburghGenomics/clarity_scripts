import argparse
import logging
import os
import re
from sys import version_info

if version_info.major == 2:
    import urlparse
else:
    from urllib import parse as urlparse

from genologics.entities import Process, Artifact
from genologics.lims import Lims

__author__ = 'tcezard'

invalid_suffixes = [
    '-QNT',
    '-CFP',
    '-NRM',
    '-IMP',
    '-SSI',
    '-ALP',
    '-CAP',
    '-PCR',
    '-CPP',
    '-LQC',
    '-DQC1',
    '-DIL1',
    '-DIL2',
    '-QPCR',
    '-CST'
]
discard_wf_name="Discard Plates EG 1.0"
sample_discard_wf_stage_name = "Find Derived Sample Plates EG 1.0"
plate_discard_wf_stage_name="Discard Plates EG 1.0"

def batch_limit(lims, list_instance, max_query=100):
    for start in range(0,len(list_instance), max_query):
        print("retrieve %s"%len(list_instance[start:start+max_query]))
        lims.get_batch(list_instance[start:start+max_query])

def fetch_all_artifacts_for_samples(lims, samples):
    """
    search for all the artifact associated with a list of samples.
    To avoid too long a query we limit to 50 samples per query
    """
    lims_ids = [s.id for s in samples]
    max_query = 50
    artifacts = []
    for start in range(0,len(lims_ids), max_query):
        artifacts.extend(lims.get_artifacts(samplelimsid=lims_ids[start:start+max_query], type="Analyte"))
    print("Found %s artifacts. Now need to batch retrieve them"%len(artifacts))
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
    Checks that the atifact has been through the given workflow.
    :return True if it has False otherwise
    """
    for w in artifact.workflow_stages:
        if w.name == workflow_step_name:
            return True
    return False


def get_workflow_stage(lims, workflow_name, stage_name=None):
    workflows=[w for w in lims.get_workflows() if w.name==workflow_name]
    if len(workflows) != 1:
        return
    if not stage_name:
        return workflows[0].stages[0]
    stages = [s for s in workflows[0].stages if s.name==stage_name]
    if len(stages) != 1:
        return
    return stages[0]



def main():
    args = _parse_args()
    r1 = urlparse.urlsplit(args.step_uri)
    server_http = '%s://%s'%(r1.scheme, r1.netloc)

    #Assume the step_uri contains the step id at the end
    step_id = r1.path.split('/')[-1]
    lims = Lims(server_http, args.username, args.password)

    #Find the Discard plate workflow uri
    discard_plate_stage = get_workflow_stage(lims, workflow_name=discard_wf_name, stage_name=plate_discard_wf_stage_name)
    print("Found discard_plate_stage_uri "+discard_plate_stage.uri)
    #get the process currently running
    p = Process(lims, id=step_id)

    #fetch the artifacts associated with the step
    step_artifacts = p.all_inputs()
    lims.get_batch(step_artifacts)

    #fetch the sample associated with these artifacts
    samples = [a.samples[0] for a in step_artifacts]
    lims.get_batch(samples)
    print("Found %d Samples"%len(samples))
    #fetch the all the artifacts associated with these samples
    step_associated_artifacts = fetch_all_artifacts_for_samples(lims, samples)
    print("Found %d step_associated_artifacts"%len(step_associated_artifacts))
    #list all the containers and retrive them
    containers = list(set([a.container for a in step_associated_artifacts]))
    batch_limit(lims, containers)
    print("Found %d containers"%len(containers))

    #filter the containers to keep the one that are valid
    valid_containers = [c for c in containers if is_valid_container(c)]
    print("Found %d valid_containers"%len(valid_containers))

    #Get all the artifacts in the valid containers and retrieve the one that were not retrieved already
    container_artifacts = set()
    for c in valid_containers:
        container_artifacts.update( set(c.placements.values()) )

    non_step_atifacts = container_artifacts.difference(set(step_associated_artifacts))
    print("Found %d non_step_atifacts"%len(non_step_atifacts))
    batch_limit(lims, non_step_atifacts)
    print("Found %d non_step_atifacts"%len(non_step_atifacts))

    artifacts_to_route = []
    container_to_route = []
    for container in valid_containers:
        route_allowed=True
        for artifact in list(container.placements.values()):
            if artifact in step_associated_artifacts or has_workflow_stage(artifact, sample_discard_wf_stage_name):
                pass
            else:
                # This container will have to wait
                route_allowed=False
        if route_allowed:
            artifacts_to_route.extend(list(container.placements.values()))
            container_to_route.append(container)
    print("Route %s containers with %s artifacts"%(len(container_to_route), len(artifacts_to_route)))
    lims.route_artifacts(artifacts_to_route, stage_uri=discard_plate_stage.uri)

    #TODO: clean up steps where the step_associated_artifacts are queued

def _parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--username', dest="username", type=str, help='The username of the person logged in')
    p.add_argument('--password', dest="password", type=str, help='The password used by the person logged in')
    p.add_argument('--step_uri', dest='step_uri', type=str, help='The uri of the step this EPP is attached to')
    return p.parse_args()


if __name__ == "__main__":
    main()
