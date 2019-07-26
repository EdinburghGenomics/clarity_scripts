#!/usr/bin/env python
import sys

from EPPs.common import GenerateHamiltonInputEPP, InvalidStepError


class GenerateHamiltonInputMakePDPMix(GenerateHamiltonInputEPP):
    """"Generate a CSV containing the necessary information to mix the PDP pool. The CSV contains a row for each
    unique output plate well with the volume to be used by the Hamilton when mixing which is the sum of the input
    NTP volumes minus 5ul or 50ul, which ever is smallest"""

    # Define the column headers that will be used in the Hamilton input file
    csv_column_headers = ['Output Plate', 'Output Well', 'Mix Volume']

    # Define the output file
    output_file_name = 'MAKE_PDP_MIX.csv'

    # Define the number of input containers that are permitted (although the file created will have up to 10 input
    # containers listed as this is the limit when creating a PDP batch and obtained from the parent process artifacts)
    _max_nb_input_containers = 1

    # Define the number of output containers that are permitted
    _max_nb_output_containers = 1

    def _generate_csv_dict(self):
        # csv_dict will be a dictionary that consists of the lines to be present in the Hamilton input file.
        csv_dict = {}

        # find all the inputs for the step that are analytes (i.e. samples and not associated files).
        # Note that the input to the step is a PDP_batch not the actual input plates so there is a 1:1 relationship
        # between the inputs and the outputs.
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
                number_libraries_in_pool = len(input_art.input_artifact_list())
                library_volume_added = input_art.udf['NTP Volume (uL)']
                dead_volume = 5

                pool_mix_volume = (number_libraries_in_pool * library_volume_added) - dead_volume
                if pool_mix_volume > 50:
                    pool_mix_volume = 50

                # assemble each line of the Hamilton input file in the correct structure for the Hamilton
                csv_line = [output.location[0].name, output_location, pool_mix_volume]

                # build a dictionary of the lines for the Hamilton input file with the output well location as key
                csv_dict[output.location[1]] = csv_line

        return csv_dict


if __name__ == '__main__':
    sys.exit(GenerateHamiltonInputMakePDPMix().run())
