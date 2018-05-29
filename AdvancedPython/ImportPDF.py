import io

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage

# Script converts a pdf application form to txt and then enters key data points into variables. A new project is created
# in Clarity LIMS into which the variables are entered.

def convert_pdf_to_txt(path):
    #code taken from stackOverflow to run the pdf to txt conversion using pdfminer package
    rsrcmgr = PDFResourceManager()
    retstr = io.StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos = set()

    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages,
                                  password=password,
                                  caching=caching,
                                  check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue()

    fp.close()
    device.close()
    retstr.close()
    return text

#create a string with the contents of the pdf
pdf_txt= convert_pdf_to_txt('application_form-controls.pdf')

#seperate the string into a list with an entry for each line of text
pdf_list=pdf_txt.split('\n')

#prints each line of text preceeded with a line number to assist with script development
for i, s in enumerate(pdf_list):
    print(str(i)+' '+s)

#for line in pdf_list:
 #   print(str(line_number)+' '+line)
  #  line_number =line_number+1

#find the key data points and add them to variables

def data_mine(the_list, substring, offset):
    for i in the_list:
        if i.startswith(substring):
            return i.replace(substring,'')


#    for i, s in enumerate(the_list):
#        if substring in s:
#           return pdf_list[i+offset]
#    return -1

enquiry_number=data_mine(pdf_list,'Enquiry Number ',4)
quote_number=data_mine(pdf_list,'Quote Number ',4)
project_number=data_mine(pdf_list,'Project Number ',4)
species=data_mine(pdf_list,'Species Scientific Name ',6)
number_samples=data_mine(pdf_list,'Total Number of Quoted Samples ',6)
principal_investigator_first_name=data_mine(pdf_list,'Principal Investigator ',13)
principal_investigator_surname=data_mine(pdf_list,'Principal Investigator ',14)
principal_investigator_address1=data_mine(pdf_list, 'Principal Investigator ',16)
principal_investigator_address2=data_mine(pdf_list, 'Principal Investigator ',17)
principal_investigator_address3=data_mine(pdf_list, 'Principal Investigator ',18)
principal_investigator_address4=data_mine(pdf_list, 'Principal Investigator ',19)
principal_investigator_address5=data_mine(pdf_list, 'Principal Investigator ',20)
principal_investigator_email=data_mine(pdf_list, 'Email ',6)
principal_investigator_number=data_mine(pdf_list, 'Contact Number ',6)

primary_first_name=data_mine(pdf_list,'PCFN ',2)
print('primary first name'+primary_first_name)
primary_surname=data_mine(pdf_list,'Surname ',2)
primary_address1=data_mine(pdf_list, 'Address Line 1 ',6)
primary_address2=data_mine(pdf_list, 'Address Line 2 ',6)
primary_address3=data_mine(pdf_list, 'Address Line 3 ',6)
primary_address4=data_mine(pdf_list, 'Address Line 4 ',6)
primary_address5=data_mine(pdf_list, 'Address Line 5 ',6)
primary_email=data_mine(pdf_list, 'Email ',6)
primary_number=data_mine(pdf_list, 'Contact Number ',6)

shipment_first_name=data_mine(pdf_list,'First Name ',2)
shipment_surname=data_mine(pdf_list,'Surname ',2)
shipment_address1=data_mine(pdf_list, 'Address Line 1 ',6)
shipment_address2=data_mine(pdf_list, 'Address Line 2 ',6)
shipment_address3=data_mine(pdf_list, 'Address Line 3 ',6)
shipment_address4=data_mine(pdf_list, 'Address Line 4 ',6)
shipment_address5=data_mine(pdf_list, 'Address Line 5 ',6)
shipment_email=data_mine(pdf_list, 'Email ',6)
shipment_number=data_mine(pdf_list, 'Contact Number ',6)

data_first_name=data_mine(pdf_list,'Data Download Access ',6)
data_surname=data_mine(pdf_list,'Data Download Access ',7)
data_email=data_mine(pdf_list, 'Email ',6)


print(principal_investigator_first_name)
print(principal_investigator_surname)



#offset = 0;
#indices = list()
#for i in range(pdf_list.count(b)):
   # indices.append(a.index(b,offset))
   # offset = indices[-1]+1





