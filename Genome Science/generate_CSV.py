from __future__ import division, print_function, absolute_import
import sys
import getopt
import glsapiutil
from xml.dom.minidom import parseString
from SampleSheetClass import *

HOSTNAME = ""
VERSION = ""
BASE_URI = ""

DEBUG = False

CACHE = {}
ARGS = {}
itemFetched = 0
itemNotFetched = 0
api = None

samplesheet = Samplesheet()


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


def log(msg):
    print(msg)


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
    print(sURI)
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

            if "QSTD A1" in name:
                sampleDict[well] = [name, "Standard", "20"]
                print("found QSTD A1")
                print(sampleDict[well][2])
            if "QSTD B1" in name: sampleDict[well] = [name, "Standard", "2"]
            if "QSTD C1" in name: sampleDict[well] = [name, "Standard", "0.2"]
            if "QSTD D1" in name: sampleDict[well] = [name, "Standard", "0.02"]
            if "QSTD E1" in name: sampleDict[well] = [name, "Standard", "0.002"]
            if "QSTD F1" in name: sampleDict[well] = [name, "Standard", "0.0002"]
            if "No Template" in name: sampleDict[well] = [name, "ntc"]
            if "QST" not in name and "No Template" not in name: sampleDict[well] = [name, "Unknown"]

    # create a list of the keys so can be used to pull the information from the sample dictionary into the second table of the input file
    sampleDictKeyList = []

    for sampleDictKey in sampleDict:
        sampleDictKeyList.append(sampleDictKey)

    # the order of the samples and standards when pulled from the XML is not in alphanumeric order so needs to be sorted
    sampleDictKeyList.sort()

    # create the header for the input file and list the standards defined in the SOP
    inputFileTxt = "Experiment Type,Standard Curve\n\nAssay Name,Reporter,Quencher,Unit,Color\nSYBR,Green,None,pM\n\nSample Name,Color\n"

    # add the list of standard names and samples names in the correct order - this is dependend on the SOP defined list of standards being present and 3 replicates for samples
    inputFileTxt = inputFileTxt + str(sampleDict["A:1"][0]) + ",\n"  # standard 1
    inputFileTxt = inputFileTxt + str(sampleDict["B:1"][0]) + ",\n"  # standard 2
    inputFileTxt = inputFileTxt + str(sampleDict["C:1"][0]) + ",\n"  # standard 3
    inputFileTxt = inputFileTxt + str(sampleDict["D:1"][0]) + ",\n"  # standard 4
    inputFileTxt = inputFileTxt + str(sampleDict["E:1"][0]) + ",\n"  # standard 5
    inputFileTxt = inputFileTxt + str(sampleDict["F:1"][0]) + ",\n"  # standard 6
    inputFileTxt = inputFileTxt + str(sampleDict["D:8"][0]) + ",\n"  # ntc
    inputFileTxt = inputFileTxt + str(sampleDict["A:4"][0]) + ",\n"  # sample 1
    if "A:5" in sampleDict: inputFileTxt = inputFileTxt + str(sampleDict["A:5"][0]) + ",\n"  # sample 2
    if "A:6" in sampleDict: inputFileTxt = inputFileTxt + str(sampleDict["A:6"][0]) + ",\n"  # sample 3
    if "A:7" in sampleDict: inputFileTxt = inputFileTxt + str(sampleDict["A:7"][0]) + ",\n"  # sample 4
    if "A:8" in sampleDict: inputFileTxt = inputFileTxt + str(sampleDict["A:8"][0]) + ",\n"  # sample 5
    if "D:4" in sampleDict: inputFileTxt = inputFileTxt + str(sampleDict["D:4"][0]) + ",\n"  # sample 6
    if "D:5" in sampleDict: inputFileTxt = inputFileTxt + str(sampleDict["D:5"][0]) + ",\n"  # sample 7
    if "D:6" in sampleDict: inputFileTxt = inputFileTxt + str(sampleDict["D:6"][0]) + ",\n"  # sample 8
    if "D:7" in sampleDict: inputFileTxt = inputFileTxt + str(sampleDict["D:7"][0]) + ",\n"  # sample 9

    # add second table header
    inputFileTxt = inputFileTxt + "\nWell Name,Sample Name,Assay Name,Assay Role,Quantity\n"

    # add the list of wells in alphanumeric order and the standards and sample names they contain
    for well in sampleDictKeyList:  # attaches the standard and sample names to the text for the input file alphanumeric order

        if "QSTD" in sampleDict[well][0]:
            inputFileTxt = inputFileTxt + well + "," + sampleDict[well][0] + ",SYBR," + sampleDict[well][1] + "," + \
                           sampleDict[well][2] + ",\n"
        else:
            inputFileTxt = inputFileTxt + well + "," + str(sampleDict[well][0]) + ",SYBR," + str(
                sampleDict[well][1]) + ",\n"

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