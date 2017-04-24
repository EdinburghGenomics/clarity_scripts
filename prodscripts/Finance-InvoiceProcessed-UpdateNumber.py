import getopt
import sys
from xml.dom.minidom import parseString

from EPPs import glsapiutil

DEBUG = False
SIMULATE = True
api = None
args = None

UDF = "bank"


def getInfo():
    ## get the XML for the process
    stepURI = args["stepURI"]
    stepsLocation = stepURI.find('steps')
    BASE_URI = stepURI[0:stepsLocation]

    pURI = BASE_URI + "processes/" + args["limsid"]
    pXML = api.getResourceByURI(pURI)
    pDOM = parseString(pXML)

    # Navigate down through XML structure to obtain project UDFS
    pnodes = pDOM.getElementsByTagName("input")

    print(pnodes)

    for p in pnodes:
        attributeURI = p.getAttribute("uri")
        print(attributeURI)

    aXML = api.getResourceByURI(attributeURI)
    aDOM = parseString(aXML)
    print(aDOM)

    anodes = aDOM.getElementsByTagName("sample")

    print(anodes)

    for a in anodes:
        sampleURI = a.getAttribute("uri")
        print(sampleURI)

    sXML = api.getResourceByURI(sampleURI)
    sDOM = parseString(sXML)
    print(sDOM)

    snodes = sDOM.getElementsByTagName("project")
    print(snodes)

    for s in snodes:
        projectURI = s.getAttribute("uri")
        print(projectURI)

    pjXML = api.getResourceByURI(projectURI)
    pjDOM = parseString(pjXML)
    print(pjDOM)

    # Set the Step UDFS with the Project UDF values
    samplesPaid = api.getUDF(pDOM, "Number of Samples Paid")
    print(samplesPaid)
    api.setUDF(pjDOM, "Number of Samples Paid", samplesPaid)

    api.updateObject(pjDOM.toxml(), projectURI)


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
    stepURI = args["stepURI"]
    apiLocation = stepURI.find('/api')
    BASE_URI = stepURI[0:apiLocation]
    print(BASE_URI)
    api = glsapiutil.glsapiutil()
    api.setHostname(BASE_URI)
    api.setVersion('v2')
    api.setup(args["username"], args["password"])

    ## at this point, we have the parameters the EPP plugin passed, and we have network plumbing
    ## so let's get this show on the road!
    getInfo()


if __name__ == "__main__":
    main()
