#!/usr/bin/env python
import sys

from EPPs.common import GenerateHamiltonInputEPP, InvalidStepError


class GenerateHamiltonInputIMPSSQC(GenerateHamiltonInputEPP):
    """"Generate a CSV containing the necessary information to transfer the fragmented sample from a covaris plate into
    an IMP plate"""
    _use_load_config = False  # prevent the loading of the config
    # Define the column headers that will be used in the Hamilton input file
    csv_column_headers = ['Input Plate', 'Input Well', 'Output IMP Plate', 'Output IMP Well', 'CFP to IMP Volume','Output SSQC Plate', 'Output SSQC Well' 'CFP to SSQC Volume','RSB to SSQC Volume']

    # Define the output file
    output_file_name = 'KAPA_TRANSFER_CFP_TO_IMP_AND_SSQC.csv'

    # Define the number of input containers that are permitted
    permitted_input_containers = 1

    # Define the number of output containers that are permitted
    permitted_output_containers = 2

    def _generate_csv_dict(self):

        # csv_dict will be a dictionary that consists of the lines to be present in the Hamilton input file.
        csv_dict = {}

        # obtain the cfp volume from the step udf
        cfp_imp_volume = self.process.udf['CFP to IMP Volume (ul)']
        cfp_SSQC_volume = self.process.udf['CFP to SSQC Volume (ul)']
        rsb_ssqc_volume = self.process.udf['RSB to SSQC Volume (ul)']

        # find all the inputs for the step that are analytes (i.e. samples and not associated files)
        for input_art in self.artifacts:
            if input_art.type == 'Analyte':
                outputs = self.process.outputs_per_input(input_art.id, Analyte=True)

                # the script is only compatible with 1 output for each input i.e. replicates are not allowed
                if len(outputs) != 2:
                    raise InvalidStepError(
                        message='Incorrect number of outputs found for %s. This step requires two outputs per input.' % (
                            input_art.name))

                # remove semi-colon from locations as this is not compatible with Hamilton Venus software
                input_location = input_art.location[1].replace(':', '')
                output_locations = []

                for output in outputs:
                    output_locations.append(output.location[1].replace(':', ''))

                # assemble each line of the Hamilton input file in the correct structure for the Hamilton

                csv_line = [input_art.container.name, input_location, outputs[0].container.name, output_locations[0],
                            cfp_imp_volume,outputs[1].container.name, output_locations[1],cfp_SSQC_volume,rsb_ssqc_volume]

                # build a dictionary of the lines for the Hamilton input file with a key that facilitates the lines being
                # by input container then column then row
                csv_dict[input_art.location[1]] = csv_line

        return csv_dict


if __name__ == '__main__':
    sys.exit(GenerateHamiltonInputIMPSSQC().run())
