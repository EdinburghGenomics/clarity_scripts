#!/usr/bin/env python
from EPPs.common import StepEPP, step_argparser
import smtplib

#DEBUG = False
#api = None
#args = None

UDF = "bank"
projectName = None
pDOM = None


class SendDataRelease(StepEPP):
    def _run(self):
        getInfo()
    def getEmailContacts(self, contact_type):
        email_contacts_file = open(args.contacts)
        email_contacts_list = email_contacts_file.readlines()
        print(email_contacts_list)

        if contact_type == 'me':
            email_sender = email_contacts_list[email_contacts_list.index('SENDER\n') + 1].replace('\n',
                                                                                                  '')  # Look for the position of the word SENDER in the list
            # and then assume the sender email is the next position and remove the \n from the end of the string

            print(email_sender)
            return email_sender

        if contact_type == 'you':
            email_recipients_list = email_contacts_list[email_contacts_list.index('RECIPIENTS\n') + 1].split(
                ',')  # look for the position of the word RECIPIENTS in the list
            # and then assume the recipients emails are the next postiion in the list then split into list with comma
            del (email_recipients_list[len(email_recipients_list) - 1])  # this removes the \n at the end of the list
            print(email_recipients_list)
            return email_recipients_list

    def sendMail(self, body, to_address):
        global projectName

        # Import the email modules we'll need
        from email.mime.text import MIMEText

        # For this example, assume that
        # the message contains only ASCII characters.
        msg = MIMEText(body)

        # me == the sender's email address
        # you == the recipient's email address
        # me = 'EGCG-Projects@ed.ac.uk'
        me = getEmailContacts('me')
        you = getEmailContacts('you')
        # you = ['EGCG-Projects@ed.ac.uk']


        msg['Subject'] = projectName + ': Edinburgh Genomics Clinical- Data Released'
        msg['From'] = me
        msg['To'] = ", ".join(you)

        # Send the message via our own SMTP server, but don't include the
        # envelope header.

        # replace "localhost" below with the IP address of the mail server
        s = smtplib.SMTP('smtp.staffmail.ed.ac.uk', 25)
        s.sendmail(me, you, msg.as_string())
        s.quit()

    def createMail(self):
        global projectName
        LIMSID = args["limsid"]
        LIMSIDSHORT = LIMSID[3:]
        ## create message of the email
        msg = "Hi,\n\nPlease release the data for the samples in " + projectName + " as shown in the link below:\n\nhttp://egclarityprod.mvm.ed.ac.uk/clarity/work-details/" + LIMSIDSHORT + ".\n\nKind regards,\nClarity X"
        sendMail(msg, "")

    def getInfo(self):
        global projectName
        global pDOM
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

        # Set the global variable "projectName" for use in the email
        pjnodes = pjDOM.getElementsByTagName("name")
        projectName = pjnodes[0].firstChild.nodeValue

        # call createMail
        createMail()


def main():
    args = _parse_args()
    action = SendDataRelease(args.step_uri, args.username, args.password, args.contacts)
    action.run()


def _parse_args():
    p = step_argparser()
    p.add_argument('--contacts', dest='contacts', type=str,
                   help='The file containing email contacts')

    return p.parse_args()


if __name__ == "__main__":
    main()
