#!/usr/bin/env python

import csv

from EPPs.common import InvalidStepError, StepEPP


class GenerateHamiltonInputQuantStudio(StepEPP):
    # define the rows and columns in the input plate (standard 96 well plate pattern)
    plate_rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    plate_columns = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
    csv_column_headers = ['Input Plate', 'Input Well', 'Output Plate', 'Output Well', 'DNA Volume', 'TE Volume']
    _max_nb_input_containers = 27
    _max_nb_output_containers = 1
    _nb_analytes_per_input = 1

    def __init__(self, argv=None):
        """ additional argument required for the location of the Hamilton input file so def __init__ customised."""
        super().__init__(argv)
        self.hamilton_input = self.cmd_args.hamilton_input

        assert self.csv_column_headers is not None, 'csv_column_headers needs to be set by the child class'
        assert self._max_nb_input_containers is not None, 'number of permitted input containers needs to be set ' \
                                                          'by the child class'
        assert self._max_nb_output_containers is not None, 'number of permitted output containers needs to be set ' \
                                                           'by the child class'

    @staticmethod
    def add_args(argparser):

        argparser.add_argument(
            '-i', '--hamilton_input', nargs='+', help='Add up to 3 file spaces in LIMS step for Hamilton inputs')

    @staticmethod
    def write_csv(filename, csv_array):
        """Write the list of list to the file provided as a csv file"""
        with open(filename, 'w', newline='') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerows(csv_array)

    def generate_csv_dict(self):
        csv_dict = {}

        for art in self.artifacts:
            if art.type == 'Analyte':
                output = self.process.outputs_per_input(art.id, Analyte=True)

                csv_line = [art.container.name, art.location[1], output[0].container.name, output[0].location[1],
                            output[0].udf['Genotyping Sample Volume (ul)'],
                            output[0].udf['Genotyping Buffer Volume (ul)']]

                csv_dict[art.container.name + art.location[1]] = csv_line
        return csv_dict

    def generate_csv_array(self):
        """
        Generate the csv array from the implemented csv dictionary.
        It sorts the csv lines by column (self.plate_columns) then row (self.plate_rows)
        """
        csv_dict = self.generate_csv_dict()

        csv_rows = [self.csv_column_headers]

        # prepare csv_row_dict so can accept rows for up to three Hamilton input files
        csv_rows_list = [csv_rows.copy(), csv_rows.copy(), csv_rows.copy()]

        well_counter = 0
        container_counter = 0
        file_counter = 0

        for container in self.input_container_names:

            if (container_counter / 9).is_integer() and container_counter > 0:
                file_counter += 1
            for column in self.plate_columns:
                for row in self.plate_rows:
                    if container + row + ":" + column in csv_dict.keys():
                        csv_rows_list[file_counter].append(csv_dict[container + row + ":" + column])
                        well_counter += 1
            container_counter += 1

        if well_counter == 0:
            raise InvalidStepError("No valid keys present in csv_dict. Key format must be row:column e.g. A:1.")

        return (csv_rows_list, file_counter)

    def _run(self):
        """Generic run that check the number of input and output container
        then creates up to three CSV files attached to the LIMS."""
        csv_array = self.generate_csv_array()
        # Create and write the Hamilton input file, this must have the hamilton_input argument as the prefix as
        # this is used by Clarity LIMS to recognise the file and attach it to the step

        self.write_csv(self.hamilton_input[0] + '-hamilton_input_1.csv', csv_array[0][0])

        if csv_array[1] > 0:
            self.write_csv(self.hamilton_input[1] + '-hamilton_input_2.csv', csv_array[0][1])

        if csv_array[1] > 1:
            self.write_csv(self.hamilton_input[2] + '-hamilton_input_3.csv', csv_array[0][2])


if __name__ == "__main__":
    GenerateHamiltonInputQuantStudio().run()
