import sys
import getopt
import glsapiutil
from xml.dom.minidom import parseString

HOSTNAME = ""
VERSION = ""
BASE_URI = ""

DEBUG = False

CACHE = {}
ARGS = {}
itemFetched = 0
itemNotFetched = 0
api = None


def setupGlobalsFromURI(uri):
    global HOSTNAME
    global VERSION
    global BASE_URI
    global STEP_URI
    tokens = uri.split("/")
    HOSTNAME = "/".join(tokens[0:3])
    VERSION = tokens[4]
    BASE_URI = "/".join(tokens[0:5]) + "/"
    STEP_URI = tokens[6]


def getObject(URI, cache=True):
    global CACHE
    global itemFetched
    global itemNotFetched

    if not cache or URI not in CACHE.keys():
        xml = api.getResourceByURI(URI)
        CACHE[URI] = xml
        itemFetched = itemFetched + 1
    else:
        itemNotFetched = itemNotFetched + 1

    return CACHE[URI]


def createSampleList():
    # need to get inputoptions from the record details screen
    sURI = BASE_URI + "processes/" + STEP_URI
    sXML = getObject(sURI)
    sDOM = parseString(sXML)

    sampleDict = {}
    name = ""

    samples = sDOM.getElementsByTagName("output")

    for sample in samples:
        if sample.getAttribute("output-type") == "ResultFile":

            artifact_uri = sample.getAttribute("uri")

            limsid = sample.getAttribute("limsid")
            aXML = getObject(artifact_uri)
            aDOM = parseString(aXML)

            name = aDOM.getElementsByTagName("name")[0].firstChild.data
            well = aDOM.getElementsByTagName("value")[0].firstChild.data
            wellParts = well.split(":")
            well = wellParts[0] + wellParts[1]

            if "QSTD A1" in name:
                sampleDict[well] = [name, "Standard", "20"]
            if "QSTD B1" in name: sampleDict[well] = [name, "std", "STANDARD", "2"]
            if "QSTD C1" in name: sampleDict[well] = [name, "std", "STANDARD", "0.2"]
            if "QSTD D1" in name: sampleDict[well] = [name, "std", "STANDARD", "0.02"]
            if "QSTD E1" in name: sampleDict[well] = [name, "std", "STANDARD", "0.002"]
            if "QSTD F1" in name: sampleDict[well] = [name, "std", "STANDARD", "0.0002"]
            if "No Template" in name: sampleDict[well] = [name, "ntc", "NTC"]
            if "QST" not in name and "No Template" not in name: sampleDict[well] = [name, "library", "UNKOWN"]

    # create a list of the keys so can be used to pull the information from the sample dictionary into the second table of the input file
    sampleDictKeyList = []

    for sampleDictKey in sampleDict:
        sampleDictKeyList.append(sampleDictKey)

    # the order of the samples and standards when pulled from the XML is not in alphanumeric order so needs to be sorted
    sampleDictKeyList.sort()

    # add the table header
    inputFileTxt = "* Chemistry = SYBR_GREEN\n* Instrument Type = sds7500fast\n* Passive Reference = ROX\n\
                   \n[Sample Setup]\nWell,Sample Name,Target Name,Task,Reporter,Quencher,Quantity,Comments"

    # add the list of wells in alphanumeric order and the standards and sample names they contain
    for well in sampleDictKeyList:  # attaches the standard and sample names to the text for the input file alphanumeric order

        if "QSTD" in sampleDict[well][0]:
            inputFileTxt = inputFileTxt + well + "," + sampleDict[well][0] + sampleDict[well][1] + sampleDict[well][2]+\
                           ",SYBR, None," + sampleDict[well][3] + ",\n"
        else:
            inputFileTxt = inputFileTxt + well + "," + sampleDict[well][0] + sampleDict[well][1] + sampleDict[well][2]+\
                           ",SYBR, None," + ",,\n"

    # Open and write to the input file - having the limsid at the beginning of the file name means it is automatically attached to that location in the step
    file = open(ARGS["filelimsid"] + "_QPCR_7500_Input.csv", "w")
    file.write(inputFileTxt)
    file.close()


def main():
    global api
    global ARGS
    global debug_instance

    opts, extraparams = getopt.getopt(sys.argv[1:], "l:u:p:f:")
    ARGS["step_type"] = "library"  # default type is always library
    for o, p in opts:
        if o == '-l':
            ARGS["limsid"] = p
        elif o == '-u':
            ARGS["username"] = p
        elif o == '-p':
            ARGS["password"] = p
        elif o == '-f':  # can be removed
            ARGS["filelimsid"] = p

    if DEBUG is True:
        for key in ARGS.keys():
            print(key + "=" + ARGS[key])

    debug_instance = 0
    setupGlobalsFromURI(ARGS["limsid"])
    api = glsapiutil.glsapiutil()
    api.setHostname(HOSTNAME)
    api.setVersion(VERSION)
    api.setup(ARGS["username"], ARGS["password"])

    createSampleList()


if __name__ == "__main__":
    main()