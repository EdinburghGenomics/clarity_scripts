#!/usr/bin/env python
import csv
import sys

from EPPs.common import StepEPP, GenerateHamiltonInputEPP, InvalidStepError


class GenerateHamiltonInputUCT(GenerateHamiltonInputEPP):
    """"Generate a CSV containing the necessary information to transfer the fragmented sample from a covaris plate into
    an IMP plate"""
    _use_load_config = False  # prevent the loading of the config
    csv_column_headers = []
    output_file_name = 'KAPA_MAKE_LIBRARIES.csv'

    def _generate_csv_dict(self):
        # csv_dict will be a dictionary that consists of the lines to be present in the Hamilton input file.
        csv_dict = {}

        # find all the inputs for the step that are analytes (i.e. samples and not associated files)
        for input in self.artifacts:
            if input.type == 'Analyte':
                output = self.process.outputs_per_input(input.id, Analyte=True)
                # the script is only compatible with 1 output for each input i.e. replicates are not allowed
                if len(output) > 1:
                    raise InvalidStepError('Multiple outputs found for an input %s. ' 
                                           'This step is not compatible with replicates.' % input.name)

                # remove semi-colon from locations as this is not compatible with Hamilton Venus software
                row, column = input.location[1].split(":")
                input_location = row + column

                # obtain well location of reagent_label (i.e. index/barcode)
                # which is stored as the first 2 or 3 characters of the label name
                adapter_well = output[0].reagent_labels[0].split("_")[0]

                # assemble each line of the Hamilton input file in the correct structure for the Hamilton
                csv_line = [input.container.name, input_location, input.name, adapter_well]
                # build a dictionary of the lines for the Hamilton input file with a key that facilitates the lines being
                # by input container then column then row
                csv_dict[input.location[1]] = csv_line
        return csv_dict


if __name__ == '__main__':
    GenerateHamiltonInputUCT().run()
