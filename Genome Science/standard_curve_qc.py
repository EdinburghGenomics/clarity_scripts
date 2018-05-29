import sys
import getopt
import glsapiutil
import xml.dom.minidom
from xml.dom.minidom import parseString
import smtplib


DEBUG = False
SIMULATE = True
api = None
args = None

UDF = "bank"


def getInfo():
	## get the XML for the process (step)
	stepURI=args["stepURI"]
	stepsLocation= stepURI.find('steps')
	BASE_URI=stepURI[0:stepsLocation]

	pURI = BASE_URI + "processes/" + args["limsid"]
	
	pXML = api.getResourceByURI(pURI)
	pDOM = parseString(pXML)


	#obtain the step UDF values
	slope = api.getUDF(pDOM, "Slope")
	print(slope)
	slope_min = api.getUDF(pDOM, "Slope Min")
	print(slope_min)
	slope_max = api.getUDF(pDOM, "Slope Max")
	print(slope_max)

	#perform the QC and set the Standard Curve QC step UDF
	if slope<slope_min or slope>slope_max:
		api.setUDF(pDOM, "Standard Curve QC", "Failed, Slope Outside of Slope Max and Min")

	else:
		api.setUDF(pDOM, "Standard Curve QC", "Passed, Slope within Min/Max criteria")

	api.updateObject( pDOM.toxml(), pURI)


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
	stepURI=args["stepURI"]
	apiLocation= stepURI.find('/api')
	BASE_URI=stepURI[0:apiLocation]
	api = glsapiutil.glsapiutil()
	api.setHostname(BASE_URI)
	api.setVersion('v2')
	api.setup(args["username"], args["password"])
	## at this point, we have the parameters the EPP plugin passed, and we have network plumbing
	## so let's get this show on the road!
	getInfo()



if __name__ == "__main__":
	main()
