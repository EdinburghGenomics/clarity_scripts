#!/usr/bin/env python
## 30/09/2016 ($VR$)
__author__ = 'vramraj'

# This script runs on a step that accepts
# an Excel sample sheet for upload. It:
# 1) Parses the sheet
# 2) For each 2D barcode UDF, searches for matching Clarity sample
# 3) Updates remaining UDFs for that sample

import argparse
import logging
import platform
import urllib.error
import urllib.parse
import urllib.request
from xml.dom.minidom import parseString, getDOMImplementation

from EPPs import glsapiutil
import xlrd
from xlrd.sheet import ctype_text

args = None
api = None

DEBUG = True

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

    # file path for text file that contains all the columns that need to be populated
    aParser.add_argument('-c', action='store', dest='columnFile', required=True)
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
                if i not in list(rawdata.keys()):
                    rawdata[i] = []

                if objtype == 'bool':
                    rawdata[i].append(bool(cell_obj.value))
                else:
                    rawdata[i].append(cell_obj.value)

    # remove first metadata entry
    HEADER.pop(0)

    rawdata.pop(sorted(rawdata.keys())[0])

    # now we have the header and sample info stored at the same index
    # and can access it accordingly

    # get all barcodes first
    barcodelist = {}
    barcodecountlist = []

    for i in sorted(rawdata.keys()):

        dataline = rawdata[i]
        if not dataline[0]:
            api.reportScriptStatus(args.stepURI, "ERROR", "2D Barcode missing for a sample, please check manifest")
            raise ValueError("2D Barcode missing for a sample, please check manifest")

        if type(dataline[0]) is float:
            dataline[0] = str(int(dataline[
                                      0]))  # DF Excel sheet parses value as float if number only so convert to int to remove decimal place .0 and then convert to str so .strip() doesn't error
            # print dataline[0]
        barcodelist[dataline[0].strip('')] = dataline
        barcodecountlist.append(dataline[0])

    for value in barcodecountlist:
        if barcodecountlist.count(value) > 1:
            raise ValueError("2D Barcode duplicated in Excel file: " + value)

    # now batch get the samples by barcode
    bArr = []
    for bcode in list(barcodelist.keys()):
        bArr.append('udf.' + urllib.parse.quote('2D Barcode') + '=' + urllib.parse.quote(bcode))

    bURI = BASE_URI + 'samples?' + '&'.join(bArr)

    bXML = api.GET(bURI)
    bDOM = parseString(bXML)

    # now we have the barcodes, generate barcode to sample map
    # generate the query string to get all the sample information
    # in one big batch

    lXML = []
    lXML.append('<ri:links xmlns:ri="http://genologics.com/ri">')
    for SS in bDOM.getElementsByTagName('sample'):
        sURI = SS.getAttribute('uri')
        lXML.append('<link uri="' + sURI + '" rel="sample"/>')
    lXML.append('</ri:links>')
    lXML = ''.join(lXML)

    mXML = api.POST(lXML, BASE_URI + "samples/batch/retrieve")
    mDOM = parseString(mXML)

    for sDOM in mDOM.getElementsByTagName('smp:sample'):

        barcode = str("")
        sName = sDOM.getElementsByTagName('name')[0].firstChild.data

        for udf in sDOM.getElementsByTagName('udf:field'):
            if udf.getAttribute('name') == '2D Barcode':
                barcode = udf.firstChild.data

        ## 04/11/2016 ($VR$): As per call, we need to do
        # sample checking only on barcode and get the info.
        # out. I moved the mapping of barcode to sample down here
        # after the barcodes were retrieved
        dataline = barcodelist[barcode]
        BARCODE_TO_SAMPLE[barcode] = sName

        if sName not in list(SAMPLE_DATA.keys()):
            SAMPLE_DATA[sName] = []

            # SAMPLE_DATA[ sName ].append( sName )
        for i in range(0, len(dataline)):
            SAMPLE_DATA[sName].append(dataline[i])

        ########

        if sName == BARCODE_TO_SAMPLE[barcode]:  # sanity check
            logging.debug(HEADER)

            for col in COLUMNS_TO_PARSE:
                colIndex = HEADER.index(col)  # get the index of the column

                logging.debug(colIndex)

                # now use the index to get the data out for this sample
                dataToBake = str(SAMPLE_DATA[sName][colIndex])
                logging.debug(str(SAMPLE_DATA[sName]))

                if len(dataToBake) > 0:
                    # logging.debug( dataToBake )
                    # add a udf child node
                    newNode = newDoc.createElement('udf:field')
                    newNode.setAttribute('name', col[col.find('/') + 1:])

                    newNode.appendChild(newDoc.createTextNode(dataToBake))
                    sDOM.appendChild(newNode)

        else:
            api.reportScriptStatus(args.stepURI, "ERROR",
                                   "Sample " + sName + " in Clarity does not have the same barcode " +
                                   BARCODE_TO_SAMPLE[barcode] + " as stated in the sample sheet.")

    # ready to bake all the DOMs back in batch

    retXML = api.POST(mDOM.toxml(), BASE_URI + "samples/batch/update")

    retDOM = parseString(retXML)

    if "exception" in retXML:
        msg = retDOM.getElementsByTagName('message')[0].firstChild.data
        print(msg)
        # logging.debug( msg )
        api.reportScriptStatus(args.stepURI, "ERROR", msg)
        raise ValueError(msg)
    return


def getParseColumns():
    global COLUMNS_TO_PARSE

    with open(args.columnFile) as ifff:
        for l in ifff:
            line = l.strip()
            if len(line) > 0 and line not in COLUMNS_TO_PARSE:
                COLUMNS_TO_PARSE.append(line)

    return


def main():
    global args
    global api

    logging.basicConfig(filename='/opt/gls/clarity/customextensions/wb.log', level=logging.DEBUG)

    args = setupArguments()

    setupGlobalsFromURI(args.stepURI)

    api = glsapiutil.glsapiutil2()
    api.setHostname(HOSTNAME)
    api.setVersion(VERSION)
    api.setup(args.username, args.password)

    getParseColumns()

    parseSampleSheet()

    return


if __name__ == '__main__':
    main()
