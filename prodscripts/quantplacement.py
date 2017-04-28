#!/usr/bin/env python
__author__ = 'dcrawford'

import string
from optparse import OptionParser
from xml.dom.minidom import parseString

from EPPs import glsapiutil


def autoPlace():
    stepdetailsXML = api.GET(args.stepURI + "/details")
    stepdetails = parseString(stepdetailsXML)

    ## Create the input output map
    iomap = {}
    for io in stepdetails.getElementsByTagName("input-output-map"):

        output = io.getElementsByTagName("output")[0]
        if output.getAttribute("type") == "Analyte":
            input = io.getElementsByTagName("input")[0]
            iomap[output.getAttribute("uri")] = input.getAttribute("uri")

    artifacts = parseString(api.getArtifacts(list(iomap.keys()) + list(iomap.values())))

    ## Map the original locations of the artfacts
    inputMap = {}
    for art in artifacts.getElementsByTagName("art:artifact"):

        artURI = art.getAttribute("uri").split("?state")[0]
        if artURI in list(iomap.values()):
            location = art.getElementsByTagName("container")[0].getAttribute("uri")
            well = art.getElementsByTagName("value")[0].firstChild.data
            inputMap[artURI] = [location, well]

    inputContainers = list(set([c[0] for c in list(
        inputMap.values())]))  # if the order of containers is going to be important, sort them here <-
    stepplacementsXML = api.GET(args.stepURI + "/placements")
    stepplacements = parseString(stepplacementsXML)
    output384 = stepplacements.getElementsByTagName("container")[0].getAttribute("uri")

    def wheredoesitgo_4plates(containerIndex, sourceWell):

        ABC = string.ascii_uppercase
        y = ABC.index(sourceWell[:1]) * 2
        if containerIndex in [3, 2]:
            y += 1
        x = int(sourceWell[2:]) * 2
        if containerIndex in [0, 2]:
            x -= 1
        return ABC[y] + ":" + str(x)

    def wheredoesitgo_1to3plates(containerIndex, sourceWell):

        ABC = string.ascii_uppercase
        y = ABC.index(sourceWell[:1])
        x = int(sourceWell[2:]) * 2
        y384 = y * 2

        if y in [ABC.index(r) for r in 'CDGH']:  # if y is row c, d, g, h,
            y384 -= 3  # move up 3 rows
        if y in [ABC.index(r) for r in 'ABCD']:  # the first 4 rows ( ABCD )
            x -= 1  # are one column to the left
        else:
            y384 -= 8  # the last 4 rows move up 8
        y384 += (4 * containerIndex)  # move down 4 rows for each new container
        return ABC[y384] + ":" + str(x)

    # writing the new placement XML from scratch
    sendplacement = [
        '<stp:placements xmlns:stp="http://genologics.com/ri/step" uri="' + args.stepURI + '/placements"><step uri="' + args.stepURI + '" rel="steps"/><output-placements>']
    for outArt in stepplacements.getElementsByTagName("output-placement"):

        outArtURI = outArt.getAttribute("uri")
        inputLocation = inputMap[iomap[outArtURI]]
        containerIndex = inputContainers.index(inputLocation[0])
        sourceWell = inputLocation[1]

        if len(inputContainers) == 4:
            value = wheredoesitgo_4plates(containerIndex, sourceWell)
        else:
            value = wheredoesitgo_1to3plates(containerIndex, sourceWell)

        sendplacement.append(
            '<output-placement uri="' + outArtURI + '"><location><container uri="' + output384 + '" limsid="' +
            output384.split("/containers/")[1] + '"/><value>' + value + '</value></location></output-placement>')
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
