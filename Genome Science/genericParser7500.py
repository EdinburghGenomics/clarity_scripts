import argparse
import xlrd
from xlrd.sheet import ctype_text
from xml.dom.minidom import parseString, getDOMImplementation
import platform
import logging
import glsapiutil
from xml.dom.minidom import parseString


# This script runs on a step that accepts
# an Excel sample sheet for upload. It:
# 1) Parses the sheet
# 2) For each 2D barcode UDF, searches for matching Clarity sample
# 3) Updates remaining UDFs for that sample


MappingColumn = 3  # In which column of the csv file will I find the artifact name
artifactUDFMap = {

    # "Column name in file" : "UDF name in Clarity",
    'UDF/ Stock Conc ng/ul': 'Stock Conc ng/uL'

}

api = None
options = None

artifactUDFResults = {}
DEBUG = True  # False

args = None
api = None

DEBUG = False

HOSTNAME = platform.node()
VERSION = 'v2'
BASE_URI = HOSTNAME + '/api/' + VERSION + '/'

COLUMNS_TO_PARSE = []

HEADER = []
SAMPLE_DATA = {}
BARCODE_TO_SAMPLE = {}


def setupArguments():
    aParser = argparse.ArgumentParser("EPP trigger script to update sample UDFs based on 2D barcode")

    aParser.add_argument('-u', action='store', dest='username', required=True)
    aParser.add_argument('-p', action='store', dest='password', required=True)
    aParser.add_argument('-s', action='store', dest='stepURI', required=True)

    # file LIMS ID for uploaded sample sheet
    aParser.add_argument('-f', action='store', dest='fileluid', required=True)

    return aParser.parse_args()


# setup globals from URI
def setupGlobalsFromURI(uri, version=None):
    global HOSTNAME
    global VERSION
    global BASE_URI

    global args  ## to fix the stepURI

    tokens = uri.split('/')

    HOSTNAME = '/'.join(tokens[0:3])

    # overwrite version if it's provided
    if version is not None:
        tokens[4] = version

    # set global to the token
    VERSION = tokens[4]

    # generate BASE_URI with overwritten version
    # if specified
    BASE_URI = '%s/' % ('/'.join(tokens[0:5]),)

    args.stepURI = '/'.join(tokens)

    # logging.debug( args.stepURI )


def getFile(aLUID):
    fileContents = ""

    ## get the details form the artifact
    aURI = BASE_URI + "artifacts/" + aLUID
    # if DEBUG: logging.debug( "Trying to lookup:" +aURI )
    aXML = api.GET(aURI)
    aDOM = parseString(aXML)

    ## get the file's details
    nodes = aDOM.getElementsByTagName("file:file")
    if len(nodes) == 1:
        fLUID = nodes[0].getAttribute("limsid")
        dURI = BASE_URI + "files/" + fLUID + "/download"
        # if DEBUG: logging.debug( "Trying to download:" + dURI )
        fileContents = api.GET(dURI)

    return fileContents


# parse the custom Edinburgh Genomics sample sheet
# and pull out UDFs values for each sample
def parseSampleSheet():
    global HEADER
    global SAMPLE_DATA
    global BARCODE_TO_SAMPLE

    newDOM = getDOMImplementation()
    newDoc = newDOM.createDocument(None, None, None)
    rawdata = {}

    # get the file from server
    raw_file = getFile(args.fileluid)

    # navigate to first Excel tab
    wb = xlrd.open_workbook(file_contents=raw_file)
    wb_sheet = wb.sheet_by_index(0)

    # get the table header out first
    # by looking at each row for the template XML-esque text
    headersection = False
    datasection = False

    for i in range(0, wb_sheet.nrows):
        rowval = enumerate(wb_sheet.row(i))
        for idx, cell_obj in rowval:
            objtype = ctype_text.get(cell_obj.ctype, 'unknown type')
            if objtype == 'text' and cell_obj.value == '<TABLE HEADER>':
                headersection = True

            elif objtype == 'text' and cell_obj.value == '</TABLE HEADER>':
                headersection = False

            elif objtype == 'text' and cell_obj.value == '<SAMPLE ENTRIES>':
                datasection = True

            elif objtype == 'text' and cell_obj.value == '</SAMPLE ENTRIES>':
                datasection = False

            if headersection is True and len(cell_obj.value) > 0:
                HEADER.append(cell_obj.value)

            if datasection is True:
                if i not in rawdata.keys():
                    rawdata[i] = []

                if objtype == 'bool':
                    rawdata[i].append(bool(cell_obj.value))
                else:
                    rawdata[i].append(cell_obj.value)

    # remove first metadata entry
    HEADER.pop(0)
    print(HEADER)
    rawdata.pop(sorted(rawdata.keys())[0])

    # now we have the header and sample info stored at the same index
    # and can access it accordingly
    results = {}
    # print("this is " +str(rawdata))
    # print(HEADER)

    for row in rawdata:
        UDFresults = {}

        for column, UDF in artifactUDFMap.items():  # add the UDF value from the file to UDF results for all the UDFs defined in artifactsUDFMap #column (spreadsheet column title) is the key in artifactUDFMap and UDF (LIMS output UDF) the value
            # print(UDF)
            print(HEADER.index(column))
            UDFresults[UDF] = rawdata[row][HEADER.index(
                column) + 1]  # HEADER.index gives a value one before the correct column in the data so have added +1
            print(UDFresults)
            results[rawdata[row][
                MappingColumn - 1]] = UDFresults  # creates an array with the artifact name (mapping column) as the key which has as the value an array with the UDF name as a key and the result in the spreadsheet as the value
            # print(results)

    # if DEBUG: print results
    # print results
    return results


def limslogic():
    artifactUDFResults = parseSampleSheet()
    # print(artifactUDFResults)
    # if DEBUG: print artifactUDFResults

    stepdetails = parseString(api.GET(args.stepURI + "/details"))  # GET the input output map
    # print api.GET( args.stepURI + "/details" )
    resultMap = {}

    for iomap in stepdetails.getElementsByTagName("input-output-map"):
        output = iomap.getElementsByTagName("output")[0]
        if output.getAttribute("output-generation-type") == 'PerInput':
            resultMap[output.getAttribute("uri")] = iomap.getElementsByTagName("input")[0].getAttribute(
                "uri")  # Create a key in resultMap array with the output artifact URI and a value with the corresponding input artifact uri
    # resultMap will map the artifact outputs to the artifact inputs


    output_artifacts = parseString(api.getArtifacts(resultMap.keys()))  # Parse the artifact XML for output artifact

    nameMap = {}

    for artDOM in output_artifacts.getElementsByTagName("art:artifact"):
        art_URI = artDOM.getAttribute("uri")

        output_name = artDOM.getElementsByTagName("name")[0].firstChild.data

        try:

            ArtifactUDFs = artifactUDFResults[
                output_name]  # Would need to change this line to input_name if the input artifact name is being matched to instead of output

            # if DEBUG: print ArtifactUDFs
            for UDF, value in ArtifactUDFs.items():  # map udfs from file to UDF
                api.setUDF(artDOM, UDF, value)
        except:
            pass

    # if DEBUG: print output_artifacts.toxml()
    r = api.POST(output_artifacts.toxml(), api.getBaseURI() + "artifacts/batch/update")
    # if DEBUG: print r


def main():
    global args
    global api

    logging.basicConfig(filename='/opt/gls/clarity/customextensions/wb.log', level=logging.DEBUG)

    args = setupArguments()

    setupGlobalsFromURI(args.stepURI)

    api = glsapiutil.glsapiutil2()
    api.setHostname(HOSTNAME)
    api.setVersion(VERSION)
    api.setURI(args.stepURI)
    api.setup(args.username, args.password)

    limslogic()

    return


if __name__ == '__main__':
    main()