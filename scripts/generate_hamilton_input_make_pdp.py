#!/usr/bin/env python
import sys

from EPPs.common import GenerateHamiltonInputEPP, InvalidStepError


class GenerateHamiltonInputMakePDP(GenerateHamiltonInputEPP):
    """"Generate a CSV containing the necessary information to create the PDP pool. Obtains lists of the input artifacts
    used to make each pool and writes a CSV line for each one of these artifacts"""

    # Define the column headers that will be used in the Hamilton input file
    csv_column_headers = ['Input Plate', 'Input Well', 'Output Plate', 'Output Well', 'Library Volume']

    # Define the output file
    output_file_name = 'MAKE_PDP.csv'

    # Define the number of input containers that are permitted (although the file created will have up to 10 input
    # containers listed as this is the limit when creating a PDP batch and obtained from the parent process artifacts)
    _max_nb_input_containers = 1

    # Define the number of output containers that are permitted
    _max_nb_output_containers = 1

    # create set of input parent containers
    parent_container_set = set()

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
                # remove semi-colon from the output location as this is not compatible with Hamilton Venus software
                output_location = output.location[1].replace(':', '')

                # obtain the list of artifacts that were used to make the pool
                parent_process_artifacts = input_art.input_artifact_list()

                # write a line of the csv for each of artifacts in the pool
                for parent_artifact in parent_process_artifacts:
                    # remove semi-colon from locations as this is not compatible with Hamilton Venus software
                    parent_input_location = parent_artifact.location[1].replace(':', '')

                    parent_input_container = parent_artifact.location[0].name

                    self.parent_container_set.add(parent_input_container)

                    # assemble each line of the Hamilton input file in the correct structure for the Hamilton

                    csv_line = [
                        parent_input_container, parent_input_location, output.location[0].name, output_location,
                        input_art.udf['NTP Volume (uL)']
                    ]
                    # build a dictionary of the lines for the Hamilton input file with a key that facilitates
                    # the lines being by input container then column then row

                    csv_dict[parent_input_container + parent_artifact.location[1]] = csv_line

        return csv_dict

    def generate_csv_array(self):
        """
        Generate the csv array from the implemented csv dictionary.
        It sorts the csv lines by column (self.plate_columns) then row (self.plate_rows)
        """
        csv_dict = self._generate_csv_dict()


        csv_rows = [self.csv_column_headers]

        counter = 0

        # create list of parent containers
        for container in sorted(self.parent_container_set):
            for column in self.plate_columns:
                for row in self.plate_rows:
                    if container + row + ":" + column in csv_dict.keys():
                        csv_rows.append(csv_dict[container + row + ":" + column])
                        counter += 1

        if counter == 0:
            raise InvalidStepError("No valid keys present in csv_dict. Key format must be container+row:column e.g. T1999P001A:1.")

        return csv_rows


if __name__ == '__main__':
    sys.exit(GenerateHamiltonInputMakePDP().run())
