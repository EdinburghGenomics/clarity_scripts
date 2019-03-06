#!/usr/bin/env python
import platform
from io import StringIO

import shutil
from numpy import unicode
from openpyxl import load_workbook, writer

from EPPs.common import StepEPP


# Scripts for parsing sample manifest for either plates, tubes or SGP tubes. The key used for the parsing is the Sample
# Name for plates and the 2D barcode for tubes/SGP tubes. The script assemnbles a dictionary of the sampe root artifacts
# using the appropriate keys. It obtains all the sample UDFs to be parsed by finding any step UDFs with the tag [Plate]
# [Tube] or [SGP]. If the sample UDFs that should be parsed needs to changed then the manifest document should be changed
# and the step UDFs updated accordingly. The step UDFs contain the column in the manifest that contains that UDF. The
# step UDF name must match the sample UDF name. Please note that assignment of UDFs in the LIMS as either numeric (int)
#or single-line text (str) is not always logical so the [Str] tag was introduced to the step UDF naming
# to convert problem data points to strings where required.
class ParseManifest(StepEPP):

    # additional argument required to obtain the file location for newly create manifest in the LIMS step
    def __init__(self, argv=None):
        super().__init__(argv)
        self.manifest = self.cmd_args.manifest

    @staticmethod
    def add_args(argparser):
        argparser.add_argument(
            '-m', '--manifest', type=str, required=True, help='Sample manifest returned by customer'
        )

    def _run(self):

        # find the MS Excel manifest
        for output in self.process.all_outputs(unique=True):
            if output.id == self.manifest:
                manifest_file = self.open_or_download_file(self.manifest, binary=True)



        # open the excel manifest
        wb=load_workbook(manifest_file)
        #wb = load_workbook(filename=manifest_file,read_only=True, data_only=True)
        ws = wb.active

        # identify the container type present in the step and assign variables appropriately. con_type is the step UDF
        # tag, key is the variable that is used for linking the sample to the matching manifest row. key column is the
        # column in the manifest that holds the key information and current_row starts as the first row in the excel
        # sheet that contains sample data and is then updated as the manifest is parsed
        if self.artifacts[0].container.type.name == '96 well plate':
            con_type = '[Plate]'
            key = 'Plate Sample Name'
            key_column = self.process.udf['Plate Sample Name']
            current_row = self.process.udf['Plate Starting Row']

        elif self.process.all_inputs()[0].container.type.name == 'rack 96 positions':
            con_type = '[Tube]'
            key = '2D Barcode'
            key_column = self.process.udf['2D Barcode']
            current_row = self.process.udf['Tube Starting Row']

        elif self.process.all_inputs()[0].container.type.name == 'SGP rack 96 positions':
            con_type = '[SGP]'
            key = '2D Barcode'
            key_column = self.process.udf['2D Barcode']
            current_row = self.process.udf['SGP Starting Row']

        # create the dictionary of sample root artifacts associated with the step based on the appropriate key for the
        # container type
        sample_dict = {}

        # need to check that only one container type present in step so assemble a set of the container types
        unique_container_types = set()

        for artifact in self.process.all_inputs(unique=True):
            if key == 'Plate Sample Name':
                sample_dict[artifact.name] = artifact.samples[0]
            if key == '2D Barcode':
                sample_dict[artifact.samples[0].udf['2D Barcode']] = artifact.samples[0]
            unique_container_types.add(artifact.container.type)

        if len(unique_container_types) > 1:
            raise ValueError('Multiple container types present in step. Only 1 container type permitted')

        # identify the non-key udfs that should be parsed for this container type
        step_udfs_to_parse = set()

        for udf in self.process.udf:
            if udf.find(con_type) >= 0:
                step_udfs_to_parse.add(udf)

        # create the list to contain the samples to be updated in a batch PUT to the API. This should match the number
        # of input artifacts
        samples_to_put = []

        key_cell = key_column + str(current_row)
        key_value = ws[key_cell].value

        while key_value:
            for udf in step_udfs_to_parse:
                #remove the container type tag from the step UDF name so can be used to find the corresponding sample UDF
                lims_udf = udf.replace(con_type, '')
                #use the column indicated in the step UDF and the current row counter to identify which cell in
                #the spreadsheet should be referenced
                udf_cell = self.process.udf[udf] + str(current_row)
                #check for udfs that need to be converted to strings as indicated by the [Str] tag in the step UDF name

                if lims_udf.find('[Str]') >=0:
                    lims_udf=lims_udf.replace('[Str]','')
                    udf_value=str(ws[udf_cell].value)

                else:
                    udf_value=ws[udf_cell].value

                #parse the data from the spreadsheet into the sample dictionary
                sample_dict[key_value].udf[lims_udf] = udf_value

            #add the modified sample to the list of modified samples to be put into the database. Raise value error if
            #sample present in manifest but not in LIMs
            try:
                samples_to_put.append(sample_dict[key_value])
            except:
                raise ValueError(key_value+" present in manifest but not present in LIMS.")

            current_row += 1
            key_cell = key_column + str(current_row)
            key_value = ws[key_cell].value


        # check that there not fewer samples in the manifest than in the LIMS

        if not len(samples_to_put) == len(self.process.all_inputs(unique=True)):
            raise ValueError('The number of samples in the step does not match the number of samples in the manifest')

        self.lims.put_batch(samples_to_put)


if __name__ == '__main__':
    ParseManifest().run()
