#!/usr/bin/env python

from EPPs.common import GenerateHamiltonInputEPP, InvalidStepError


class GenerateHamiltonInputUCT(GenerateHamiltonInputEPP):
    """"Generate a CSV containing the necessary information for the KAPA make libraries method"""
    _use_load_config = False  # prevent the loading of the config
    csv_column_headers = ['Input Plate', 'Input Well', 'Sample Name', 'Adapter Well']
    output_file_name = 'KAPA_MAKE_LIBRARIES.csv'

    # Define the number of input containers that are permitted
    permitted_input_containers = 1

    # Define the number of output containers that are permitted
    permitted_output_containers = 1

    def _generate_csv_dict(self):
        # csv_dict will be a dictionary that consists of the lines to be present in the Hamilton input file.
        csv_dict = {}

        # find all the inputs for the step that are analytes (i.e. samples and not associated files)

        for art in self.artifacts:

            if art.type == 'Analyte':
                output = self.process.outputs_per_input(art.id, Analyte=True)
                # the script is only compatible with 1 output for each input i.e. replicates are not allowed
                if len(output) > 1:
                    raise InvalidStepError('Multiple outputs found for an input %s. '
                                           'This step is not compatible with replicates.' % art.name)

                # remove semi-colon from locations as this is not compatible with Hamilton Venus software
                row, column = art.location[1].split(":")
                input_location = row + column

                # obtain well location of reagent_label (i.e. index/barcode)
                # which is stored as the first 2 or 3 characters of the label name
                adapter_well = output[0].reagent_labels[0].split("_")[0]

                # assemble each line of the Hamilton input file in the correct structure for the Hamilton
                csv_line = [art.container.name, input_location, art.name, adapter_well]

                # build a dictionary of the lines for the Hamilton input file with a key that facilitates the lines being
                # by input container then column then row
                csv_dict[art.location[1]] = csv_line
        return csv_dict


if __name__ == '__main__':
    GenerateHamiltonInputUCT().run()
