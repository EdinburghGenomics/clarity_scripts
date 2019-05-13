#!/usr/bin/env python
import sys

from EPPs.common import GenerateHamiltonInputEPP, InvalidStepError


class GenerateHamiltonInputMakePDP(GenerateHamiltonInputEPP):
    """"Generate a CSV containing the necessary information to create the PDP pool"""

    # Define the column headers that will be used in the Hamilton input file
    csv_column_headers = ['Input Plate', 'Input Well', 'Output Plate', 'Output Well', 'Library Volume']

    # Define the output file
    output_file_name = 'MAKE_PDP.csv'

    #Define the number of input containers that are permitted
    _max_nb_input_containers = 10

    #Define the number of output containers that are permitted
    _max_nb_output_containers = 1

    def _generate_csv_dict(self):
        # csv_dict will be a dictionary that consists of the lines to be present in the Hamilton input file.
        csv_dict = {}

        # find all the inputs for the step that are analytes (i.e. samples and not associated files)
        for input_art in self.artifacts:
            if input_art.type == 'Analyte':
                outputs = self.process.outputs_per_input(input_art.id, Analyte=True)
                # the script is only compatible with 1 output for each input i.e. replicates are not allowed
                if len(outputs) > 1:
                    raise InvalidStepError('Multiple outputs found for an input %s. '
                                           'This step is not compatible with replicates.' % input_art.name)
                output = outputs[0]

                # remove semi-colon from locations as this is not compatible with Hamilton Venus software
                input_location = input_art.location[1].replace(':', '')
                output_location = output.location[1].replace(':', '')

                # assemble each line of the Hamilton input file in the correct structure for the Hamilton
                csv_line = [
                    input_art.container.name, input_location, output.container.name, output_location,
                               self.process.udf['Library Volume (uL)']
                ]
                # build a dictionary of the lines for the Hamilton input file with a key that facilitates
                # the lines being by input container then column then row
                csv_dict[input_art.location[1]] = csv_line

        return csv_dict


if __name__ == '__main__':
    sys.exit(GenerateHamiltonInputMakePDP().run())
