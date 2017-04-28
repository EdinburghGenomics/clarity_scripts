import getopt
import sys

from genologics.entities import Process
from genologics.lims import Lims

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
    LIMSID = args["limsid"]
    usernameargs = args["username"]
    passwordargs = args["password"]
    stepURI = args["stepURI"]
    apiLocation = stepURI.find('/api')
    BASE_URI = stepURI[0:apiLocation]
    l = Lims(baseuri=BASE_URI, username=usernameargs, password=passwordargs)
    p = Process(l, id=LIMSID)
    artifacts = p.all_inputs()
    for art in artifacts:
        sample = art.samples[0]
        submitted_art = sample.artifact
        print("deployedagain2")
        if art.samples[0].udf.get("Proceed To SeqLab") == True:
            stage = get_workflow_stage(l, "PreSeqLab EG 6.0", "Sequencing Plate Preparation EG 2.0")
            l.route_artifacts([submitted_art], stage_uri=stage.uri)
            print("deployedagain")

        #if sample.udf.get("Species") == "Homo sapiens" or sample.udf.get("Species") == "Human":
            #stage = get_workflow_stage(l, "QuantStudio EG1.0", "QuantStudio Plate Preparation EG1.0")
            #l.route_artifacts([submitted_art], stage_uri=stage.uri)


def main():
    global api
    global args

    args = {}

    opts, extraparams = getopt.getopt(sys.argv[1:], "l:s:u:p:")

    for o, p in opts:
        if o == '-l':
            args["limsid"] = p
        elif o == '-s':
            args["stepURI"] = p
        elif o == '-u':
            args["username"] = p
        elif o == '-p':
            args["password"] = p

    ## at this point, we have the parameters the EPP plugin passed, and we have network plumbing
    ## so let's get this show on the road!
    assignWorkflow()


if __name__ == "__main__":
    main()
