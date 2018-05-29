#! usr/bin/env python
""" Reading qPCR ECO result csv file for data
"""

__author__ = "Matt Bishop"
__version__ = "DEV Version 1"

import pyclarity_lims
from pyclarity_lims.lims import Lims
from pyclarity_lims.entities import Process
import getopt
import sys
import csv
import itertools
import re


def getInfo():
    # set the args
    limsid = args["limsid"]
    uname = args["username"]
    pword = args["password"]
    stepURI = args["stepURI"]
    fname = args["filename"]
    # Create base uri (http://localhost:9080/)
    apiLocation = stepURI.find('api')
    baseURI = stepURI[0:apiLocation]

    # Create LIMS instance
    lims = Lims(baseURI, uname, pword)

    # Get process (this is a pyclarity-lims 'process' entity)
    processID = Process(lims, id=limsid)

    # Globals
    outputIDList = []
    runMetricsRowStart = 7
    runMetricsRowEnd = 9
    runDataRowStart = 10
    exptNameRowStart = 4
    exptNameRowEnd = 6
    # UDF variables
    slopeUDF = 0
    slopeUDFQC = ''
    rSquaredUDF = 0
    rSquaredQCUDF = ''
    interceptUDF = 0
    standardCurveUDF = 0
    effPercentUDF = 0
    effPercentQCUDF = ''
    exptFilenameUDF = ''
    std20CqMeanUDF = 0
    std20CqMeanQCUDF = ''
    std2CqMeanUDF = 0
    std2CqMeanQCUDF = ''
    std02CqMeanUDF = 0
    std02CqMeanQCUDF = ''
    std002CqMeanUDF = 0
    std002CqMeanQCUDF = ''
    std0002CqMeanUDF = 0
    std0002CqMeanQCUDF = ''
    std00002CqMeanUDF = 0
    std00002CqMeanQCUDF = ''
    ntcCqMeanUDF = 0
    ntcCqMeanQCUDF = ''
    CqQCUDF = ''
    CqMeanQCUDF = ''
    qpcrMolarityUDF = 0

    # Reading csv of ECO output file
    with open(fname, 'r') as csvfile:
        exptNameRead = csv.DictReader(itertools.islice(csvfile, exptNameRowStart, exptNameRowEnd))
        for row in exptNameRead:
            exptFilenameUDF = row['Experiment Name']
            processID.udf['Experiment File Name'] = exptFilenameUDF
    with open(fname, 'r') as csvfile:
        metricsDataRead = csv.DictReader(itertools.islice(csvfile, runMetricsRowStart, runMetricsRowEnd))
        # loop through rows for overall run metrics: r2, slope, intercept, efficiency percent,
        # set QC values for standard curve QC (slope between min-max), efficiency percent QC
        for row in metricsDataRead:
            effPercentUDF = float(row['Efficiency %'])
            processID.udf['Efficiency Percent'] = effPercentUDF
            if 90 < effPercentUDF < 110:
                effPercentQCUDF = 'PASS'
            else:
                effPercentQCUDF = 'FAIL'
            processID.udf['Efficiency Percent QC'] = effPercentQCUDF
            rSquaredUDF = float(row['R2'])
            processID.udf['R-Squared'] = rSquaredUDF
            if rSquaredUDF > 0.995:
                rSquaredQCUDF = 'PASS'
            else:
                rSquaredQCUDF = 'FAIL'
            processID.udf['R-Squared QC'] = rSquaredQCUDF
            sl = re.search('=(.+?)x', row['Equation'])
            slopeUDF = float(sl.group(1))
            processID.udf['Slope'] = slopeUDF
            if processID.udf['Slope Min'] < slopeUDF < processID.udf['Slope Max']:
                slopeUDFQC = 'PASS'
            else:
                slopeUDFQC = 'FAIL'
            processID.udf['Slope QC'] = slopeUDFQC

            ic = re.search('x\+(.*)', row['Equation'])
            interceptUDF = float(ic.group(1))
            processID.udf['Intercept'] = interceptUDF

    # Will need the list of sample names here to use as a search
    sampleNameList = []
    # Will need a list of standards to check Cq difference
    standardCqMeans = []
    with open(fname, 'r') as csvfile:
        runDataRead = csv.DictReader(itertools.islice(csvfile, runDataRowStart, None))
        # loop through rows
        for row in runDataRead:
            if row['Assay Role'] == "Unknown" and row['Exclude'] == "":
                sampleNameList.append(row['Sample Name'])

            elif row['Assay Role'] == "NTC":
                ntcCqMeanUDF = float(row['Cq Mean'])
                processID.udf['NTC Cq Mean'] = ntcCqMeanUDF
                if ntcCqMeanUDF > processID.udf['NTC Cq Limit']:
                    ntcCqMeanQCUDF = 'PASS'
                else:
                    ntcCqMeanQCUDF = 'FAIL'
                processID.udf['NTC Cq Mean QC'] = ntcCqMeanQCUDF
            elif row['Sample Name'] == 'STD 20':
                std20CqMeanUDF = float(row['Cq Mean'])
                processID.udf['STD 20 Cq Mean'] = std20CqMeanUDF
            elif row['Sample Name'] == 'STD 2':
                std2CqMeanUDF = float(row['Cq Mean'])
                processID.udf['STD 2 Cq Mean'] = std2CqMeanUDF
            elif row['Sample Name'] == 'STD 0.2':
                std02CqMeanUDF = float(row['Cq Mean'])
                processID.udf['STD 0.2 Cq Mean'] = std02CqMeanUDF
            elif row['Sample Name'] == 'STD 0.02':
                std002CqMeanUDF = float(row['Cq Mean'])
                processID.udf['STD 0.02 Cq Mean'] = std002CqMeanUDF
            elif row['Sample Name'] == 'STD 0.002':
                std0002CqMeanUDF = float(row['Cq Mean'])
                processID.udf['STD 0.002 Cq Mean'] = std0002CqMeanUDF
            elif row['Sample Name'] == 'STD 0.0002':
                std00002CqMeanUDF = float(row['Cq Mean'])
                processID.udf['STD 0.0002 Cq Mean'] = std00002CqMeanUDF

        # Compare the separation of the standards (need to be within 3.3+-0.3)
        if 3.00 < (std2CqMeanUDF - std20CqMeanUDF) < 3.60:
            std2CqMeanQCUDF = 'PASS'
        else:
            std2CqMeanQCUDF = 'FAIL'
        std20CqMeanQCUDF = 'PASS'
        processID.udf['STD 20 Cq Mean QC'] = std20CqMeanQCUDF
        processID.udf['STD 2 Cq Mean QC'] = std2CqMeanQCUDF
        if 3.00 < (std02CqMeanUDF - std2CqMeanUDF) < 3.60:
            std02CqMeanQCUDF = 'PASS'
        else:
            std02CqMeanQCUDF = 'FAIL'
        processID.udf['STD 0.2 Cq Mean QC'] = std02CqMeanQCUDF
        if 3.00 < (std002CqMeanUDF - std02CqMeanUDF) < 3.60:
            std002CqMeanQCUDF = 'PASS'
        else:
            std002CqMeanQCUDF = 'FAIL'
        processID.udf['STD 0.02 Cq Mean QC'] = std002CqMeanQCUDF
        if 3.00 < (std0002CqMeanUDF - std002CqMeanUDF) < 3.60:
            std0002CqMeanQCUDF = 'PASS'
        else:
            std0002CqMeanQCUDF = 'FAIL'
        processID.udf['STD 0.02 Cq Mean QC'] = std002CqMeanQCUDF
        if 3.00 < (std00002CqMeanUDF - std0002CqMeanUDF) < 3.60:
            std00002CqMeanQCUDF = 'PASS'
        else:
            std00002CqMeanQCUDF = 'FAIL'
        processID.udf['STD 0.002 Cq Mean QC'] = std0002CqMeanQCUDF
        processID.udf['STD 0.0002 Cq Mean QC'] = std00002CqMeanQCUDF

        processID.put()

        # Need to get the inputs so that values can be assigned to the samples
        rInputs = processID.all_inputs()

        print('Sample Names: ', sampleNameList)
        for s in sampleNameList:
            for i in rInputs:
                # Get outputs for inputs - this is the user input data
                rOutputPerInput = processID.outputs_per_input(i.id, ResultFile=True, SharedResultFile=False,
                                                              Analyte=False)
                # Get the artifact ID
                for op in rOutputPerInput:
                    if s == op.name:
                        with open(fname, 'r') as csvfile:
                            runDataRead = csv.DictReader(itertools.islice(csvfile, runDataRowStart, None))
                            # loop through rows
                            for row in runDataRead:
                                if row['Sample Name'] == s:
                                    print(s, ': Well: ', row['Well'], 'Cq: ', row['Cq'], 'Cq Mean: ', row['Cq Mean'],
                                          'Qty. Mean: ', row['Qty. Mean'])
                                    qpcrMolarityUDF = (float(row['Qty. Mean']) * 452 / 650) * 10
                                    i.udf['qPCR Molarity (nM)'] = qpcrMolarityUDF
                                    i.udf['qPCR Quantity Mean'] = float(row['Qty. Mean'])
                                    i.udf['Cq'] = float(row['Cq'])

                                    if abs(float(row['Cq']) - float(row['Cq Mean'])) < 0.5:
                                        CqQCUDF = 'PASS'
                                    else:
                                        CqQCUDF = 'FAIL'
                                    i.udf['Cq QC'] = CqQCUDF
                                    if float(row['Cq Mean']) > 8:
                                        CqMeanQCUDF = 'PASS'
                                    else:
                                        CqMeanQCUDF = 'FAIL'
                                    i.udf['Cq Mean QC'] = CqMeanQCUDF
                                    i.put()


def main():
    global args
    args = {}
    opts, extraparams = getopt.getopt(sys.argv[1:], "l:s:u:p:f:")

    for o, p in opts:
        if o == '-l':
            args["limsid"] = p
        elif o == '-s':
            args["stepURI"] = p
        elif o == '-u':
            args["username"] = p
        elif o == '-p':
            args["password"] = p
        elif o == '-f':
            args["filename"] = p

    limsid = args["limsid"]
    stepURI = args["stepURI"]
    uname = args["username"]
    pword = args["password"]
    fname = args["filename"]
    # all five options obtained from the call to the api when the process initiated

    getInfo()


if __name__ == "__main__":
    main()
