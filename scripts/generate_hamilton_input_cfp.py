#!/usr/bin/env python
import csv
import re
import sys

from EPPs.common import StepEPP, step_argparser


class GenerateHamiltonInputUPL(StepEPP):
    """"Generate a CSV containing the necessary information to normalise the sample in a NRM plate"""

    # additional argument required for the location of the Hamilton input file so def _init_ customised
    def __init__(self, step_uri, username, password, log_file, hamilton_input,shared_drive_path):
        super().__init__(step_uri, username, password, log_file)
        self.hamilton_input = hamilton_input
        self.shared_drive_path = shared_drive_path

    def _run(self):
        # csv_dict will be a dictionary that consists of the lines to be present in the Hamilton input file. These are
        # then sorted into correct order and added to the csv_array which is used to write the file
        csv_dict = {}
        csv_array = []

        # define the column headers that will be used in the Hamilton input file and add to the csv_array to be
        # used to write the file
        csv_column_headers = ['Input Plate', 'Input Well', 'Output Plate', 'Output Well', 'DNA Volume',
                              'RSB Barcode', 'RSB Volume']
        csv_array.append(csv_column_headers)

        # find the lot number, i.e. barcode, of the RSB reagent.
        RSB_template = "LP[0-9]{7}-RSB"

        reagent_lots = list(self.process.step.reagent_lots)

        for lot in reagent_lots:
            if re.match(RSB_template, lot.lot_number):
                rsb_barcode = lot.lot_number

        # define the sets for listing the unique input and output containers
        unique_input_containers = set()
        unique_output_containers = set()

        # obtain all of the inputs for the step
        all_inputs = self.process.all_inputs()

        # find all the inputs for the step that are analytes (i.e. samples and not associated files)
        for input in all_inputs:
            if input.type == 'Analyte':
                output = self.process.outputs_per_input(input.id, Analyte=True)
                # the script is only compatible with 1 output for each input i.e. replicates are not allowed
                if len(output) > 1:
                    print('Multiple outputs found for an input %s. This step is not compatible with replicates.' % (
                        input.name))
                    sys.exit(1)

                # build a list of the unique input containers for checking that no more than 1 is present due
                # Build a list of unique output containers as no more than 1 plate
                unique_input_containers.add(input.container.name)

                unique_output_containers.add(output[0].container.name)

                #remove semi-colon from locations as this is not compatible with Hamilton Venus software
                row,column=input.location[1].split(":")
                input_location=row+column
                row,column=output[0].location[1].split(":")
                output_location=row+column

                # assemble each line of the Hamilton input file in the correct structure for the Hamilton
                csv_line = [input.container.name, input_location, output[0].container.name, output_location,
                            input.udf['CFP_DNA_Volume (uL)'], rsb_barcode, input.udf['CFP_RSB_Volume (uL)']]
                # build a dictionary of the lines for the Hamilton input file with a key that facilitates the lines being
                # by input container then column then row
                csv_dict[input.location[1]] = csv_line

        # check the number of input containers
        if len(unique_input_containers) > 1:
            print('Maximum number of input plates is 1. There are %s output plates in the step.' % (
                str(len(unique_input_containers))))
            sys.exit(1)
        # check the number of output containers
        if len(unique_output_containers) > 1:
            print('Maximum number of output plates is 1. There are %s output plates in the step.' % (
                str(len(unique_output_containers))))
            sys.exit(1)
        # define the rows and columns in the input plate (standard 96 well plate pattern)
        rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        columns = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']

        # add the lines to the csv_array that will be used to write the Hamilton input file
        for column in columns:
            for row in rows:
                if row + ":" + column in csv_dict.keys():
                    csv_array.append(csv_dict[row + ":" + column])

        # create and write the Hamilton input file, this must have the hamilton_input argument as the prefix as this is used by
        # Clarity LIMS to recognise the file and attach it to the step
        with open(self.hamilton_input + '-hamilton_input.csv', 'w') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerows(csv_array)

        with open(self.shared_drive_path +'KAPA_MAKE_CFP.csv','w') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerows(csv_array)

def main():
    p = step_argparser()
    p.add_argument('-i', '--hamilton_input', type=str, required=True, help='Hamilton input file generated by LIMS')
    p.add_argument('-d', '--shared_drive_path', type=str, required=True,
                   help='Shared drive path location for Hamilton input file')
    args = p.parse_args()

    action = GenerateHamiltonInputUPL(args.step_uri, args.username, args.password, args.log_file, args.hamilton_input, args.shared_drive_path)
    action.run()


if __name__ == '__main__':
    main()
