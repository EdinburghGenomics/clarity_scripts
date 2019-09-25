#!/usr/bin/env python
from openpyxl.styles import Font

from EPPs.common import SendMailEPP
from datetime import date
from openpyxl import Workbook
import csv

class GenerateHumanTissueReport(SendMailEPP):
    #today's date required for file name and email
    todays_date = str(date.today())
    #csv report needs to be accessible throughout object
    report_path='Human_Tissue_Report_'+todays_date+'.csv'
    report_xls='Human_Tissue_Report_'+todays_date+'.xlsx'

    #batch limit function reduces the number of samples in each batch call to prevent server resource error (modified from prepare_discard_plate.py)
    def batch_limit(self, list_instance, max_query=100):
        submitted_samples_batch = []
        for start in range(0, len(list_instance), max_query):
            submitted_samples_batch= submitted_samples_batch + self.lims.get_batch(list_instance[start:start + max_query])
        return submitted_samples_batch

    def get_human_artifacts(self):
        #find all the human submitted samples in the LIMS
        submitted_samples = self.lims.get_samples(udf={'Species': 'human'}) +self.lims.get_samples(udf={'Species':'Homo sapiens'})
        #it is too slow querying each sample for udf and project details so make batch calls to the LIMS using batch_limit function
        submitted_samples_batch = self.batch_limit(submitted_samples)
        return submitted_samples_batch

    def create_report(self):
        #obtain human submitted samples still stored
        submitted_samples_batch = self.get_human_artifacts()
        #create a list of lists to be used to write the csv containing the report
        csv_contents = []
        csv_column_headers=['PI','Sample Type', 'Project Name', 'Submitted Sample Name', 'REC#', 'Freezer', 'Shelf']
        csv_contents.append(csv_column_headers)
        #obtain the project and udf information for each sample and append it to the csv list. Don't append if sample has been destroyed.
        for sample in submitted_samples_batch:
            freezer_location = sample.udf.get('Freezer')
            if freezer_location != 'Sample Destroyed':
                rec=sample.project.udf.get('REC#')
                rec_committee=sample.project.udf.get('Organisation providing ethical consent approval')
                shelf=sample.udf.get('Shelf')
                csv_contents.append(['Edinburgh Genomics', 'DNA', sample.project.name,sample.name,rec,rec_committee,freezer_location,shelf])

        #write the csv file
        with open(self.report_path,'w',newline='') as file:
            writer = csv.writer(file)
            writer.writerows(csv_contents)

    def create_excel_report(self):
        submitted_samples_batch = self.get_human_artifacts()

        wb = Workbook()
        ws = wb.active
        ws['A1']='PI'
        ws['A1'].font= Font(bold=True)
        ws.column_dimensions['A'].width = 20
        ws['B1']='Sample Type'
        ws['B1'].font = Font(bold=True)
        ws.column_dimensions['B'].width = 15
        ws['C1']='Project Name'
        ws['C1'].font = Font(bold=True)
        ws.column_dimensions['C'].width = 15
        ws['D1']='Submitted Sample Name'
        ws['D1'].font = Font(bold=True)
        ws.column_dimensions['D'].width = 20
        ws['E1']='REC#'
        ws['E1'].font = Font(bold=True)
        ws.column_dimensions['E'].width = 40
        ws['F1']='Ethics Committee'
        ws['F1'].font = Font(bold=True)
        ws.column_dimensions['F'].width = 20
        ws['G1']='Freezer'
        ws['G1'].font = Font(bold=True)
        ws.column_dimensions['G'].width = 20
        ws['H1']='Shelf'
        ws['H1'].font = Font(bold=True)
        ws.column_dimensions['G'].width = 20

        #start the row counter at 2 as the headings are in row 1
        row_counter=2

        for sample in submitted_samples_batch:
            freezer_location = sample.udf.get('Freezer')
            if freezer_location != 'Sample Destroyed':
                shelf=sample.udf.get('Shelf')
                ws['A'+str(row_counter)] = 'Edinburgh Genomics'
                ws['B'+str(row_counter)] = 'DNA'
                ws['C'+str(row_counter)] = sample.project.name
                ws['D'+str(row_counter)] = sample.name
                ws['E'+str(row_counter)] = sample.project.udf.get('REC#')
                ws['F' + str(row_counter)] = sample.project.udf.get('Organisation providing ethical consent approval')
                ws['G'+str(row_counter)] = freezer_location
                ws['H'+str(row_counter)] = shelf
            row_counter+=1

        wb.save(filename=self.report_xls)

    def send_email(self):
        msg_subject="Human Tissue Report - Edinburgh Genomics - "+self.todays_date
        msg="Hi,\n\nPlease find attached the Human Tissue Report from Edinburgh Genomics Clinical for %s.\n\nKind Regards,\nEdinburgh Genomics" % self.todays_date
        self.send_mail(msg_subject,msg, attachments=[self.report_path], config_name='human_tissue')



    def _run(self):
        #self.create_report()
        self.create_excel_report()
        #self.send_email()

if __name__ == '__main__':
    GenerateHumanTissueReport().run()