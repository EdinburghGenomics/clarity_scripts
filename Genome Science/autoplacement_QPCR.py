__author__ = 'Daniel Forth based on dcrawords autoplacement 1 to 1 for 96 well'

import string
from optparse import OptionParser
import glsapiutil
from xml.dom.minidom import parseString


def autoPlace():
    stepdetailsXML = api.GET(args.stepURI + "/details")
    stepdetails = parseString(stepdetailsXML)

    ## Create the input output map. This searches throught he step details xml and finds the output artifacts assigned to the
    ## input artifacts by Clarity. It then places the artifact URIs them in a dictionary with the output URI as a key and the input URI
    ## as the value. It then parses the XMl from all of the URIs in the dictionary.
    iomap = {}
    for io in stepdetails.getElementsByTagName("input-output-map"):

        output = io.getElementsByTagName("output")[0]
        # XML structure varies depending on the type of step and output types
        # if output.getAttribute( "type" ) == "Analyte":
        if output.getAttribute("output-generation-type") == "PerInput":
            input = io.getElementsByTagName("input")[0]
            iomap[output.getAttribute("uri")] = input.getAttribute("uri")

    artifacts = parseString(api.getArtifacts(iomap.keys() + iomap.values()))

    ## Acquire the sample names from the input artifacts - art in artifacts is just the key from the dictionary and ignores the values
    inputNames = {}
    for art in artifacts.getElementsByTagName("art:artifact"):

        artURI = art.getAttribute("uri").split("?state")[0]
        if artURI in iomap.values():
            name = art.getElementsByTagName("name")[0].firstChild.data

            inputNames[artURI] = [name]

    stepplacementsXML = api.GET(args.stepURI + "/placements")
    stepplacements = parseString(stepplacementsXML)
    outputContainerURI = stepplacements.getElementsByTagName("container")[0].getAttribute("uri")
    # obtain the output container type name to determine the pattern of placement 48 well or 96
    outputContainer = parseString(api.GET(outputContainerURI))
    outputContainerName = outputContainer.getElementsByTagName("type")[0].getAttribute("name")

    # define the wells that the standards should be placed in, as decided by the lab, each standard requires a counter for assigning replicates
    standardsLocation = {
        'QSTD A1': ['A:1', 'A:2', 'A:3', 0],
        'QSTD B1': ['B:1', 'B:2', 'B:3', 0],
        'QSTD C1': ['C:1', 'C:2', 'C:3', 0],
        'QSTD D1': ['D:1', 'D:2', 'D:3', 0],
        'QSTD E1': ['E:1', 'E:2', 'E:3', 0],
        'QSTD F1': ['F:1', 'F:2', 'F:3', 0],
        'No Template Control': ['G:1', 'G:2', 'G:3', 0],
    }
    # check the type of output container and determine the appropriate standard location and wellList
    wellList = []
    if "96 well plate" in outputContainerName:
        standardsLocation = {
            'QSTD A1': ['A:1', 'A:2', 'A:3', 0],
            'QSTD B1': ['B:1', 'B:2', 'B:3', 0],
            'QSTD C1': ['C:1', 'C:2', 'C:3', 0],
            'QSTD D1': ['D:1', 'D:2', 'D:3', 0],
            'QSTD E1': ['E:1', 'E:2', 'E:3', 0],
            'QSTD F1': ['F:1', 'F:2', 'F:3', 0],
            'No Template Control': ['G:1', 'G:2', 'G:3', 0],
        }
        wellList = ['H:1', 'H:2', 'H:3', 'A:4', 'B:4', 'C:4', 'D:4', 'E:4', 'F:4', 'G:4', 'H:4', 'A:5', 'B:5', 'C:5',
                    'D:5', 'E:5', 'F:5', 'G:5', 'H:5', 'A:6', 'B:6', 'C:6', 'D:6', 'E:6', 'F:6', 'G:6', 'H:6', 'A:7',
                    'B:7', 'C:7', 'D:7', 'E:7', 'F:7', 'G:7', 'H:7', 'A:8', 'B:8', 'C:8', 'D:8', 'E:8', 'F:8', 'G:8',
                    'H:8', 'A:9', 'B:9', 'C:9', 'D:9', 'E:9', 'F:9', 'G:9', 'H:9', 'A:10', 'B:10', 'C:10', 'D:10',
                    'E:10', 'F:10', 'G:10', 'H:10', 'A:11', 'B:11', 'C:11', 'D:11', 'E:11', 'F:11', 'G:11', 'H:11',
                    'A:12', 'B:12', 'C:12', 'D:12', 'E:12', 'F:12', 'G:12', 'H:12', ]
        if len(iomap) > 96:
            raise ValueError("Too many samples in step. Maximum is 25 samples + 7 controls for 7500 QPCR")
    elif "Eco 48 QPCR" in outputContainerName:
        standardsLocation = {
            'QSTD A1': ['A:1', 'A:2', 'A:3', 0],
            'QSTD B1': ['B:1', 'B:2', 'B:3', 0],
            'QSTD C1': ['C:1', 'C:2', 'C:3', 0],
            'QSTD D1': ['D:1', 'D:2', 'D:3', 0],
            'QSTD E1': ['E:1', 'E:2', 'E:3', 0],
            'QSTD F1': ['F:1', 'F:2', 'F:3', 0],
            'No Template Control': ['D:8', 'E:8', 'F:8', 0],
        }

        wellList = ['A:4', 'B:4', 'C:4', 'D:4', 'E:4','F:4', 'A:5', 'B:5', 'C:5', 'D:5', 'E:5', 'F:5', 'A:6', 'B:6', 'C:6', 'D:6', 'E:6',
                    'F:6', 'A:7', 'B:7', 'C:7', 'D:7', 'E:7', 'F:7', 'A:8', 'B:8', 'C:8', 'D:8', 'E:8', 'F:8', ]
        if len(iomap) > 48:
            raise ValueError("Too many samples in step. Maximum is 9 samples + 7 controls for Eco QPCR")

    wellCounter = 0

    # writing the new placement XML from scratch
    sendplacement = [
        '<stp:placements xmlns:stp="http://genologics.com/ri/step" uri="' + args.stepURI + '/placements"><step uri="' + args.stepURI + '" rel="steps"/><output-placements>']

    for outArt in stepplacements.getElementsByTagName("output-placement"):

        outArtURI = outArt.getAttribute("uri")

        inputData = inputNames[iomap[outArtURI]]

        if standardsLocation.get(inputData[0], "0") is not "0":

            standardCounter = standardsLocation[inputData[0]][3]

            value = standardsLocation[inputData[0]][standardCounter]
            standardCounter = standardCounter + 1
            standardsLocation[inputData[0]][3] = standardCounter

        else:

            value = wellList[wellCounter]
            wellCounter = wellCounter + 1

        sendplacement.append(
            '<output-placement uri="' + outArtURI + '"><location><container uri="' + outputContainerURI + '" limsid="' +
            outputContainerURI.split("/containers/")[
                1] + '"/><value>' + value + '</value></location></output-placement>')
    sendplacement.append('</output-placements></stp:placements>')

    r = api.POST(''.join(sendplacement), args.stepURI + "/placements")


def setupArguments():
    Parser = OptionParser()
    Parser.add_option('-u', "--username", action='store', dest='username')
    Parser.add_option('-p', "--password", action='store', dest='password')
    Parser.add_option('-s', "--stepURI", action='store', dest='stepURI')

    return Parser.parse_args()[0]


api = None


def main():
    global args
    args = setupArguments()

    global api
    api = glsapiutil.glsapiutil2()
    api.setURI(args.stepURI)
    api.setup(args.username, args.password)

    autoPlace()


if __name__ == "__main__":
    main()
