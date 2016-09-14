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


def assign_to_create_prod_cst_workflow(usename, password, step_uri):
    r1 = urlparse.urlsplit(step_uri)
    server_http = '%s://%s' % (r1.scheme, r1.netloc)
    l = Lims(server_http, username=usename, password=password)

    # Assume the step_uri contains the step id at the end
    step_id = r1.path.split('/')[-1]

    # Get the process from the id
    p = Process(l, id=step_id)
    # Get the output artifacts
    artifacts = p.all_outputs(unique=True, resolve=True)
    #Find the workflow stage
    stage = get_workflow_stage(l, "TruSeq PCR-Free DNA Sample Prep", "Create Production CST Batch")
    # route the artifacts
    l.route_artifacts(artifacts, stage_uri=stage.uri)


def main():

    p = argparse.ArgumentParser()
    p.add_argument('--username', dest="username", type=str, required=True, help='The username of the person logged in')
    p.add_argument('--password', dest="password", type=str, required=True, help='The password used by the person logged in')
    p.add_argument('--step_uri', dest='step_uri', type=str, required=True, help='The uri of the step this EPP is attached to')
    args = p.parse_args()

    assign_to_create_prod_cst_workflow(args.username, args.password, args.step_uri)


if __name__ == "__main__":
    main()