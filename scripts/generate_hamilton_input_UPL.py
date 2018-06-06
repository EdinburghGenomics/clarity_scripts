#!/usr/bin/env python
import csv

from EPPs.common import StepEPP, step_argparser


class GenerateHamiltonInputUPL(StepEPP):
    """"Generate a CSV containing the necessary information to batch up ot 9 User Prepared Library receipt
    into one DCT plate. Requires input and output plate containers and well positions from LIMS. Volume to be pipetted
    is taken from the step UDF "DNA Volume (uL)"""

    def __init__(self, step_uri, username, password, log_file, hamilton_input):
        super().__init__(step_uri, username, password, log_file)
        self.hamilton_input = hamilton_input

    def _run(self):
        all_inputs = self.process.all_inputs()
        csv_dict={}
        csv_array = []
        csv_column_headers = ['Input Plate', 'Input Well', 'Output Plate', 'Output Well', 'DNA Volume', 'TE Volume']
        csv_array.append(csv_column_headers)

        for input in all_inputs:
            if input.type == 'Analyte':
                output = self.process.outputs_per_input(input.id, Analyte=True)
                output_container = output[0].container.name
                output_well = output[0].location[1]

                csv_line = [input.container.name, input.location[1], output_container, output_well,
                            self.process.udf['DNA Volume (uL)'], '0']
                csv_dict[input.location[1]]=csv_line
                #csv_array.append(csv_line)
        print(csv_dict)

        rows=['A','B','C','D','E','F','G','H']
        columns=['1','2','3','4','5','6','7','8','9','10','11','12']

        for row in rows:
            for column in columns:
                if csv_dict[row+":"+column]:
                    csv_array.append(csv_dict[row+":"+column])

        file_name = self.hamilton_input + '-hamilton_input.csv'

        with open(file_name, 'w') as csvFile:
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
