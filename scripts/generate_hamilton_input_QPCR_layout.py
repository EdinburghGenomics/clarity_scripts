#!/usr/bin/env python
import csv
import re
import sys

from EPPs.common import StepEPP, step_argparser


class GenerateHamiltonInputUPL(StepEPP):
    """"Generate a 2 row CSV containing the necessary information to for the Make QPCR Hamilton app - number of samples
    UCT plate barcode, DIL1 plate barcode and DIL2 plate barcode - 1st row is column headers, 2nd row is data"""

    # additional argument required for the location of the Hamilton input file so def _init_ customised
    def __init__(self, step_uri, username, password, log_file, hamilton_input):
        super().__init__(step_uri, username, password, log_file)
        self.hamilton_input = hamilton_input

    def _run(self):
        # csv_dict will be a dictionary that consists of the lines to be present in the Hamilton input file. These are
        # then sorted into correct order and added to the csv_array which is used to write the file
        csv_dict = {}
        csv_array = []

        # define the column headers that will be used in the Hamilton input file and add to the csv_array to be
        # used to write the file
        csv_column_headers = ['UCT-DCT Plate Barcode', 'UCT-DCT Well', 'QPCR Plate Barcode', 'QPCR Well-1',
                              'QPCR Well-2', 'QPCR Well-3', 'DIL1 Plate Barcode', 'DIL2 Plate Barcode',
                              'QSTD Plate Barcode', 'QMX Barcode']
        csv_array.append(csv_column_headers)

        # find the DIL1 and DIL2 barcodes
        DIL1_template = "LP[0-9]{7}-DIL1"
        DIL1_barcode = self.process.udf['DIL1 Plate Barcode']
        DIL2_template = "LP[0-9]{7}-DIL2"
        DIL2_barcode = self.process.udf['DIL2 Plate Barcode']

        # check that DIL1 and DIL2 plate barcodes have the correct format
        if not re.match(DIL1_template, DIL1_barcode):
            print(
                "%s is not a valid DIL1 container name. Container names must match %s" % (DIL1_barcode, DIL1_template))
            sys.exit(1)

        if not re.match(DIL1_template, DIL1_barcode):
            print(
                "%s is not a valid DIL2 container name. Container names must match %s" % (DIL2_barcode, DIL2_template))
            sys.exit(1)

        # find the corresponding lot number i.e. barcode for the QMX and QSTD.
        QMX_template = "LP[0-9]{7}-QMX"
        QSTD_template = "LP[0-9]{7}-QSTD"

        reagent_lots = list(self.process.step.reagent_lots)

        for lot in reagent_lots:
            if re.match(QMX_template, lot.lot_number):
                QMX_barcode = lot.lot_number
            if re.match(QSTD_template, lot.lot_number):
                QSTD_barcode = lot.lot_number

        # define the sets for listing the unique input and output containers
        unique_input_containers = set()
        unique_output_containers = set()

        # obtain all of the inputs for the step
        all_inputs = self.process.all_inputs()
        input_analytes = set()

        # find all the inputs for the step that are analytes (i.e. samples and not associated files) then add them to a set
        for input in all_inputs:
            if input.type == 'Analyte':
                input_analytes.add(input)

                output = self.process.outputs_per_input(input.id, ResultFile=True)
                # the script is only compatible with 1 output for each input i.e. replicates are not allowed
                if len(output) != 3:
                    print(
                        '%s outputs found for an input %s. 3 replicates required' % ((str(len(output))), (input.name)))
                    sys.exit(1)
                # build a list of the unique input containers for checking that no more than 1 is present and for importing
                # container name into CSV

                unique_input_containers.add(input.container.name)

                # build a list of the unique output containers for checking that no more than 1 is present and for importing
                # container name into CSV

                unique_output_containers.add(output[0].container.name)

                # assemble each line of the Hamilton input file in the correct structure for the Hamilton

                csv_line = [input.container.name, input.location[1], output[0].container.name, output[0].location[1],
                            output[1].location[1], output[2].location[1], DIL1_barcode, DIL2_barcode, QSTD_barcode,
                            QMX_barcode]

                # build a dictionary of the lines for the Hamilton input file with a key that facilitates the lines being
                # by input container then column then row
                csv_dict[input.location[1]] = csv_line

        # check the number of inputs
        if len(input_analytes) > 3:
            print('Maximum number of input samples is 23. There are %s input samples in the step.' % (
                str(len(input_analytes))))
            #sys.exit(1)

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
        csvFile.close()


def main():
    p = step_argparser()
    p.add_argument('-i', '--hamilton_input', type=str, required=True, help='Hamilton input file generated by LIMS')
    args = p.parse_args()

    action = GenerateHamiltonInputUPL(args.step_uri, args.username, args.password, args.log_file, args.hamilton_input)
    action.run()


if __name__ == '__main__':
    main()
