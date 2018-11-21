#!/usr/bin/env python

import re
import sys
from operator import itemgetter

from EPPs.common import GenerateHamiltonInputEPP, InvalidStepError


class GenerateHamiltonInputQPCR(GenerateHamiltonInputEPP):
    """"Generate a CSV containing the necessary information to for the Make QPCR 1 to 24 samples Hamilton method"""
    _use_load_config = False  # prevent the loading of the config

    # define the column headers that will be used in the Hamilton input file and add to the csv_array to be
    # used to write the file
    csv_column_headers = ['Sample Name', 'UCT-DCT Plate Barcode', 'UCT-DCT Well', 'QPCR Plate Barcode', 'QPCR Well-1',
                          'QPCR Well-2', 'QPCR Well-3', 'DIL1 Plate Barcode', 'DIL2 Plate Barcode',
                          'QSTD Plate Barcode', 'QMX Barcode']

    # Define the output file
    output_file_name = 'MAKE_QPCR-1_TO_24_INPUT.csv'

    # Define the number of input containers that are permitted
    permitted_input_containers = 1

    # Define the number of output containers that are permitted
    permitted_output_containers = 1

    def _run(self):
        # libraries_csv_dict_dict will be a dictionary that consists of the lines to be present in the Hamilton input file for the input libraries.
        # standards_csv_dict will be a dictionary that consists of the lines to be present in the Hamilton input file for the standards. These are
        # then sorted into correct order and added to the csv_array which is used to write the file
        libraries_csv_dict = {}
        standards_csv_dict = {}
        csv_array = []




        # find the DIL1 and DIL2 barcodes
        DIL1_template = "LP[0-9]{7}-DIL1"
        DIL1_barcode = self.process.udf['DIL1 Plate Barcode']
        DIL2_template = "LP[0-9]{7}-DIL2"
        DIL2_barcode = self.process.udf['DIL2 Plate Barcode']

        # check that DIL1 and DIL2 plate barcodes have the correct format
        if not re.match(DIL1_template, DIL1_barcode):
            raise InvalidStepError(message='%s is not a valid DIL1 container name. Container names must match %s' % (
            DIL1_barcode, DIL1_template))

        if not re.match(DIL1_template, DIL1_barcode):
            raise InvalidStepError(message='%s is not a valid DIL2 container name. Container names must match %s' % (
            DIL2_barcode, DIL2_template))

        # find the corresponding lot number i.e. barcode for the QMX and QSTD.
        qmx_template = "LP[0-9]{7}-QMX"
        qstd_template = "LP[0-9]{7}-QSTD"

        qstd_barcode = ""
        qmx_barcode = ""

        reagent_lots = list(self.process.step.reagent_lots)

        for lot in reagent_lots:
            if re.match(qmx_template, lot.lot_number):
                qmx_barcode = lot.lot_number
            if re.match(qstd_template, lot.lot_number):
                qstd_barcode = lot.lot_number

        if not qmx_barcode:
            raise InvalidStepError(
                message='qPCR Master Mix (QMX) lot not selected. Please select in "Reagent Lot Tracking" at top of step.')

        if not qstd_barcode:
            raise InvalidStepError(
                message='QSTD Plate lot not selected. Please select in "Reagent Lot Tracking" at top of step.')

        # check that no more than 31 inputs present in the step. 7 standards and a maximum of 24 samples.
        if len(self.artifacts) > 24:
            raise InvalidStepError(
                message='% samples and standards present in step. There should be 7 standards and up to 24 samples present' % (
                    len(self.artifacts)))

        # find all the inputs for the step that are analytes (i.e. samples and not associated files) then add them to a set
        for input_art in self.artifacts:
            if input_art.type == 'Analyte':

                # remove semi-colon from the input location as this is not compatible with Hamilton Venus software
                input_location = input_art.location[1].replace(':', '')

                output = self.process.outputs_per_input(input_art.id, ResultFile=True)
                # the script is only compatible with 3 outputs for each input i.e. replicates are not allowed
                if len(output) != 3:
                    raise InvalidStepError(message='%s outputs found for an input %s. 3 replicates required' %
                                                   ((str(len(output))), input_art.name))

                # output locations i.e. wells in the QPCR plate need to appear in numerical order so they appear in column order
                # in the QPCR well-X columns.
                output_locations = []
                counter = 0
                #there are 3 replicates so 3 output locations, capture the row and column for each location in a list of lists
                while counter <= 2:
                    row,column=output[counter].location[1].split(":")
                    output_locations.append([row,int(column)])
                    counter = counter+1

                #use 'sorted' and 'itemgetter' to sort the output locations first by the row then by the column
                output_locations=sorted(output_locations, key=itemgetter(0,1))

                #reset count to 0
                counter = 0

                #reassemble the well location strings as [row][column] without a semi-colon
                output_locations_final=[]
                while counter <= 2:
                    output_locations_final.append(output_locations[counter][0]+str(output_locations[counter][1]))
                    counter = counter+1

                #assemble each line of the Hamilton input file in the correct structure for the Hamilton
                csv_line = [input_art.name,input_art.container.name,input_location,output[0].container.name,
                            output_locations_final[0], output_locations_final[1], output_locations_final[2],
                            DIL1_barcode, DIL2_barcode,qstd_barcode,qmx_barcode]

                # build a dictionary of the lines for the Hamilton input file with a key that facilitates the lines being
                # by input container then column then row. Standards do not have an input well location and are appended
                # at the end of the file in alphanumeric order. No Template Control must be the last row in the file.
                if input_art.location[1] == "1:1":
                    if input_art.name == "No Template Control":
                        no_template_control = csv_line
                    else:
                        standards_csv_dict[input_art.name] = csv_line
                else:
                    libraries_csv_dict[input_art.location[1]] = csv_line

        def generate_csv_array(self):
            csv_rows = [self.csv_column_headers]
            # add the lines to the csv_array that will be used to write the Hamilton input file for the input libraries
            for column in self.plate_columns:
                for row in self.plate_rows:
                    if row + ":" + column in libraries_csv_dict.keys():
                        csv_rows.append(libraries_csv_dict[row + ":" + column])

            # standards do not have plate and well information in the LIMS. Append them to the end of the csv_array in alphanumeric order
            # of sample name
            for standard in sorted(standards_csv_dict):
                csv_rows.append(standards_csv_dict[standard])

            # add the No Template Control to the end of the file
            csv_rows.append(no_template_control)

            return csv_rows

if __name__ == '__main__':
    GenerateHamiltonInputQPCR().run()
