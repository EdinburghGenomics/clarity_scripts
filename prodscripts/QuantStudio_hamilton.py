__author__ = 'dcrawford'

from EPPs import glsapiutil
from xml.dom.minidom import parseString
from optparse import OptionParser

api = None

def limslogic():

    def writecsv():

        content = ['Input Plate, Input Well, Output Plate, Output Well']

        for art in sortedArtifacts:

            inputContainerName = ConName[ inputMap[ art ][0] ]
            inputWell = inputMap[ art ][1]
            outputArt = iomap[ art ]
            outputContainerName = ConName[ inputMap[ outputArt ][0] ]
            outputWell = inputMap[ outputArt ][1]

            content.append( ','.join( [ inputContainerName,
                                        inputWell,
                                        outputContainerName,
                                        outputWell ]) )

        content = '\n'.join( content )
        file = open( options.resultfile , "w" )
        file.write( content )
        file.close()

    # Gather the required Data from LIMS
    stepdetailsXML = api.GET( options.stepURI + "/details" )
    stepdetails = parseString( stepdetailsXML )

    ## Create the input output map
    iomap = {}
    for io in stepdetails.getElementsByTagName( "input-output-map" ):
        output = io.getElementsByTagName( "output" )[0]
        if output.getAttribute( "type" ) == "Analyte":
            input = io.getElementsByTagName( "input" )[0]
            iomap[ input.getAttribute( "uri" ) ] = output.getAttribute( "uri" )

    artifacts = parseString( api.getArtifacts( list(iomap.keys()) + list(iomap.values())) )

    ## Map the locations of the artfacts
    inputMap = {}
    for art in artifacts.getElementsByTagName( "art:artifact" ):
        artURI = art.getAttribute( "uri" ).split("?state")[0]
        location = art.getElementsByTagName( "container" )[0].getAttribute( "uri" )
        well = art.getElementsByTagName( "value" )[0].firstChild.data
        inputMap[ artURI ] = [ location, well ]

    # Gather the names of the containers
    ConName = {}
    for c in parseString( api.getContainers( list( set([ c[0] for c in list(inputMap.values()) ])) )).getElementsByTagName("con:container"):
        ConName[ c.getAttribute( "uri" ) ] = c.getElementsByTagName("name")[0].firstChild.data

    ## sort the artifacts by the container first, then the well location
    def con_well(x):
        w = inputMap[x][1]
        if len( inputMap[x][1] ) == 3:
            #w = w[:2] + "0" + w[2:] ## row first
            w = "0" + w[2:] + w[:2] ## column first
        return inputMap[x][0] + w
    sortedArtifacts = sorted( list(iomap.keys()), key=con_well)

    writecsv()

def setupArguments():

    Parser = OptionParser()
    Parser.add_option('-u', "--username", action='store', dest='username')
    Parser.add_option('-p', "--password", action='store', dest='password')
    Parser.add_option('-s', "--stepURI", action='store', dest='stepURI')
    Parser.add_option('-r', "--resultfile", action='store', dest='resultfile')

    return Parser.parse_args()[0]

def main():

    global options
    options = setupArguments()

    global api
    api = glsapiutil.glsapiutil2()
    api.setURI( options.stepURI )
    api.setup( options.username, options.password )

    limslogic()

if __name__ == "__main__":
    main()
