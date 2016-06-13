import sys
import getopt

if sys.version_info.major == 2:
    import urlparse
else:
    from urllib import parse as urlparse

from genologics.lims import Lims
from genologics.entities import Process

HOSTNAME = ""
VERSION = ""
BASE_URI = ""

api = None
args = None


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


def assignWorkflow():
    usernameargs = args["username"]
    passwordargs = args["password"]
    step_uri = args["uri"]
    r1 = urlparse.urlsplit(step_uri)
    server_http = '%s://%s' % (r1.scheme, r1.netloc)

    # Assume the step_uri contains the step id at the end
    step_id = r1.path.split('/')[-1]
    l = Lims(server_http, username=usernameargs, password=passwordargs)
    # Get the process from the id
    p = Process(l, id=step_id)
    # Get the artifacts
    artifacts = p.all_inputs()
    #Find the workflow stage
    stage = get_workflow_stage(l, "TruSeq PCR-Free DNA Sample Prep", "Create Production CST Batch")
    # route the artifacts
    l.route_artifacts(artifacts, stage_uri=stage.uri)


def main():
    global api
    global args

    args = {}

    opts, extraparams = getopt.getopt(sys.argv[1:], "l:u:p:")

    for o, p in opts:
        if o == '-l':
            args["uri"] = p
        elif o == '-u':
            args["username"] = p
        elif o == '-p':
            args["password"] = p

    ## at this point, we have the parameters the EPP plugin passed, and we have network plumbing
    ## so let's get this show on the road!
    assignWorkflow()


if __name__ == "__main__":
    main()
