import argparse
import sys

if sys.version_info.major == 2:
    import urlparse
else:
    from urllib import parse as urlparse

from genologics.lims import Lims
from genologics.entities import Process




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


def assign_workflow_stage(usename, password, step_uri, workflow_name, stage_name, source):
    r1 = urlparse.urlsplit(step_uri)
    server_http = '%s://%s' % (r1.scheme, r1.netloc)
    l = Lims(server_http, username=usename, password=password)

    # Assume the step_uri contains the step id at the end
    step_id = r1.path.split('/')[-1]

    # Get the process from the id
    p = Process(l, id=step_id)
    # Get the output artifacts
    if source == 'input':
        artifacts = p.all_inputs(unique=True, resolve=True)
    elif source == 'output':
        artifacts = p.all_outputs(unique=True, resolve=True)
    elif source == 'submitted':
        artifacts = list(frozenset([s.artifact for a in p.all_inputs() for s in a.samples]))
    #Find the workflow stage
    if stage_name:
        stage = get_workflow_stage(l, workflow_name, stage_name)
    else:
        stage = get_workflow_stage(l, workflow_name)
    # route the artifacts
    l.route_artifacts(artifacts, stage_uri=stage.uri)


def main():

    p = argparse.ArgumentParser()
    p.add_argument('--username', dest="username", type=str, required=True,
                   help='The username of the person logged in.')
    p.add_argument('--password', dest="password", type=str, required=True,
                   help='The password used by the person logged in.')
    p.add_argument('--step_uri', dest='step_uri', type=str, required=True,
                   help='The uri of the step this EPP is attached to.')
    p.add_argument('--workflow', dest='workflow', type=str, required=True,
                   help='The name of the workflow we should route the artifacts to.')
    p.add_argument('--stage', dest='stage', type=str,
                   help='The name of the stage in the workflow we should route the artifacts to.')
    p.add_argument('--source', dest='source', type=str, required=True, choice=['input', 'output', 'submitted'],
                   help='The name of the stage in the workflow we should route the artifacts to.')

    args = p.parse_args()

    assign_workflow_stage(args.username, args.password, args.step_uri, args.workflow_name, args.stage_name, args.source)


if __name__ == "__main__":
    main()
