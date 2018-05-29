import sys
import getopt
#import glsapiutil
import xml.dom.minidom
from xml.dom.minidom import parseString
import smtplib

DEBUG = False
SIMULATE = False
api = None
args = None

projectName = None


def getInfo():
    global projectName

    # assign the BASE_URI
    ## get the XML for the process
    stepURI = args["stepURI"]
    stepsLocation = stepURI.find('steps')
    BASE_URI = stepURI[0:stepsLocation]

    pURI = BASE_URI + "processes/" + args["limsid"]

    pXML = api.getResourceByURI(pURI)

    pDOM = parseString(pXML)

    # Navigate down through XML structure to obtain project UDFS
    pnodes = pDOM.getElementsByTagName("input")

    for p in pnodes:
        attributeURI = p.getAttribute("uri")

    aXML = api.getResourceByURI(attributeURI)
    aDOM = parseString(aXML)

    anodes = aDOM.getElementsByTagName("sample")

    for a in anodes:
        sampleURI = a.getAttribute("uri")

    sXML = api.getResourceByURI(sampleURI)
    sDOM = parseString(sXML)

    snodes = sDOM.getElementsByTagName("project")

    for s in snodes:
        projectURI = s.getAttribute("uri")

    pjXML = api.getResourceByURI(projectURI)
    pjDOM = parseString(pjXML)

    pjnodes = pjDOM.getElementsByTagName("name")

    projectName = pjnodes[0].firstChild.nodeValue

    createMail()


def sendMail(body, to_address):
    global projectName
    # Import the email modules we'll need
    from email.mime.text import MIMEText

    # For this example, assume that
    # the message contains only ASCII characters.
    msg = MIMEText(body)

    # me == the sender's email address
    # you == the recipient's email address
    me = 'EGCG-Projects@ed.ac.uk'
    you = ['EGCG-Projects@ed.ac.uk', 'caron.barker@ed.ac.uk', 'e.heap@ed.ac.uk', 'cathlene.eland@ed.ac.uk']

    msg['Subject'] = projectName + ': FluidX Dispatch Complete'
    msg['From'] = me
    msg['To'] = ", ".join(you)

    # Send the message via our own SMTP server, but don't include the
    # envelope header.

    # replace "localhost" below with the IP address of the mail server
    s = smtplib.SMTP('smtp.staffmail.ed.ac.uk', 25)
    s.sendmail(me, you, msg.as_string())
    s.quit()


def createMail():
    global projectName
    LIMSID = args["limsid"]
    LIMSIDSHORT = LIMSID[3:]
    ## create message of the email
    msg = "Hi,\n\nFluidX dispatch has been completed: " + projectName + ". Please check the following link for details:\n\n http://egclaritydev.mvm.ed.ac.uk:8080/clarity/work-details/" + LIMSIDSHORT + ".\n\nKind regards,\nClarity X"
    if SIMULATE is True:
        print
        msg
    else:
        sendMail(msg, "")


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
    # assign the host name
    stepURI = args["stepURI"]
    apiLocation = stepURI.find('/api')
    HOST_NAME = stepURI[0:apiLocation]

    api = glsapiutil.glsapiutil()
    api.setHostname(HOST_NAME)
    api.setVersion("v2")
    api.setup(args["username"], args["password"])
    ## at this point, we have the parameters the EPP plugin passed, and we have network plumbing
    ## so let's get this show on the road!
    getInfo()


if __name__ == "__main__":
    main()
