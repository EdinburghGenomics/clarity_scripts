#!/usr/bin/env python
import sys

import re

from EPPs.common import GenerateHamiltonInputEPP, InvalidStepError


class GenerateHamiltonInputQPCRDilution(GenerateHamiltonInputEPP):
    # define the column headers that will be used in the Hamilton input file and add to the csv_array to be
    # used to write the file
    csv_column_headers = ['Input Plate', 'Input Well', 'Output Plate', 'Output Well', 'Sample Volume', 'Buffer Barcode',
                          'Buffer Volume']

    # Define the output file
    output_file_name = 'QPCR DILUTION.csv'

    # Define the number of input containers that are permitted
    _max_nb_input_containers = 1

    # Define the number of output containers that are permitted
    _max_nb_output_containers = 1

    def _generate_csv_dict(self):
        # csv_dict will be a dictionary that consists of the lines to be present in the Hamilton input file.
        csv_dict = {}

        # find the lot number, i.e. barcode, of the RSB reagent.
        buffer_template = "LP[0-9]{7}-RSB"
        reagent_lots = list(self.process.step.reagent_lots)

        buffer_barcode = None
        for lot in reagent_lots:
            if re.match(buffer_template, lot.lot_number):
                buffer_barcode = lot.lot_number

        if not buffer_barcode:
            raise InvalidStepError('Please assign buffer lot before generating Hamilton input.')

        # find all the inputs for the step that are analytes (i.e. samples and not associated files)
        for input_art in self.artifacts:
            if input_art.type == 'Analyte':
                output = self.process.outputs_per_input(input_art.id, ResultFile=True)[0]

                # remove semi-colon from locations as this is not compatible with Hamilton Venus software
                input_location = input_art.location[1].replace(':', '')
                output_location = output.location[1].replace(':', '')

                # assemble each line of the Hamilton input file in the correct structure for the Hamilton
                csv_line = [
                    input_art.container.name, input_location, output.container.name, output_location,
                    self.process.udf['DCT Volume (ul)'], buffer_barcode, output.udf['RSB Volume (ul)']
                ]
                # build a dictionary of the lines for the Hamilton input file with a key that facilitates
                # the lines being by input container then column then row
                csv_dict[input_art.location[1]] = csv_line

        return csv_dict

if __name__ == '__main__':
    sys.exit(GenerateHamiltonInputQPCRDilution().run())