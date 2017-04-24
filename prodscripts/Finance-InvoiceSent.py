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

    samplesQuoted = api.getUDF(pjDOM, "Number of Quoted Samples")
    print(samplesQuoted)
    samplesInvoiced = api.getUDF(pjDOM, "Number of Samples Invoiced")
    print(samplesInvoiced)
    samplesPaid = api.getUDF(pjDOM, "Number of Samples Paid")
    print(samplesPaid)
    invoiceName = api.getUDF(pjDOM, "Invoice Recipient Name")
    print(invoiceName)
    invoicePhone = api.getUDF(pjDOM, "Invoice Recipient Phone")
    print(invoicePhone)
    invoiceEmail = api.getUDF(pjDOM, "Invoice Recipient Email")
    print(invoiceEmail)
    invoiceAddress1 = api.getUDF(pjDOM, "Invoice Address Line 1")
    print(invoiceAddress1)
    invoiceAddress2 = api.getUDF(pjDOM, "Invoice Address Line 2")
    print(invoiceAddress2)
    invoiceAddress3 = api.getUDF(pjDOM, "Invoice Address Line 3")
    print(invoiceAddress3)
    invoiceAddress4 = api.getUDF(pjDOM, "Invoice Address Line 4")
    print(invoiceAddress4)
    invoiceAddress5 = api.getUDF(pjDOM, "Invoice Address Line 5")
    print(invoiceAddress5)

    # Set the Step UDFS with the Project UDF values
    api.setUDF(pDOM, "Number of Quoted Samples", samplesQuoted)
    api.setUDF(pDOM, "Number of Samples Invoiced", samplesInvoiced)
    api.setUDF(pDOM, "Number of Samples Paid", samplesPaid)
    api.setUDF(pDOM, "Invoice Recipient Name", invoiceName)
    api.setUDF(pDOM, "Invoice Recipient Phone", invoicePhone)
    api.setUDF(pDOM, "Invoice Recipient Email", invoiceEmail)
    api.setUDF(pDOM, "Invoice Address Line 1", invoiceAddress1)
    api.setUDF(pDOM, "Invoice Address Line 2", invoiceAddress2)
    api.setUDF(pDOM, "Invoice Address Line 3", invoiceAddress3)
    api.setUDF(pDOM, "Invoice Address Line 4", invoiceAddress4)
    api.setUDF(pDOM, "Invoice Address Line 5", invoiceAddress5)

    api.updateObject(pDOM.toxml(), pURI)


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
    api.setup(args["username"], args[
        "password"])  ## at this point, we have the parameters the EPP plugin passed, and we have network plumbing
    ## so let's get this show on the road!
    getInfo()


if __name__ == "__main__":
    main()
