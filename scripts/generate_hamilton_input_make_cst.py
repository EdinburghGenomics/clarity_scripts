#!/usr/bin/env python
import sys

from EPPs.common import GenerateHamiltonInputEPP, InvalidStepError


class GenerateHamiltonInputMakeCST(GenerateHamiltonInputEPP):
    """Generat a csv input file for Hamilton for running Make CST method"""

    # Define the number of input containers that are permitted
    _max_nb_input_containers = 1

    # Define the number of output containers that are permitted
    _max_nb_output_containers = 1

    # Define the output file
    output_file_name = 'MAKE_CST.csv'

    csv_column_headers = ['Input Container',
                          'Input Well',
                          'Output Container',
                          'Output Well',
                          'EPX1 Barcode',
                          'EPX1',
                          'EPX2 Barcode',
                          'EPX2',
                          'EPX3 Barcode',
                          'EPX3',
                          'EPX Master Mix',
                          'NaOH Barcode'
                          'NaOH',
                          'Tris-HCL Barcode'
                          'Tris-HCL',
                          'PhiX Barcode'
                          'PhiX',
                          'Library']

    # create set of input parent containers
    parent_container_set = set()

    def get_reagent_barcodes(self):
        # find the lot number, i.e. barcode, of the reagent.
        RSB_template = "LP[0-9]{7}-RSB"
        reagent_lots = list(self.process.step.reagent_lots)
        reagent_barcodes = {}
        expected_reagent_names = ['EPX1', 'EPX2', 'EPX3', 'EPX Master Mix','NaOH', 'Tris-HCL', 'PhiX']

        for lot in reagent_lots:
            reagent_barcodes[lot.name] = lot.lot_number

        for expected_reagent_name in expected_reagent_names:
            if not reagent_barcodes[expected_reagent_name]:
                raise InvalidStepError(
                    message='Please assign ' + expected_reagent_name + ' lot before generating Hamilton input.')

        return reagent_barcodes

    def _generate_csv_dict(self):
        # csv_dict will be a dictionary that consists of the lines to be present in the Hamilton input file.
        csv_dict = {}
        reagent_barcodes = self.get_reagent_barcodes()

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
                output_location = output.location[1].replace(':', '')

                # obtain the list of artifacts that were used to make the pool
                parent_process_artifacts = input_art.input_artifact_list()

                for parent_artifact in parent_process_artifacts:
                    # remove semi-colon from locations as this is not compatible with Hamilton Venus software
                    parent_input_location = parent_artifact.location[1].replace(':', '')

                    parent_input_container = parent_artifact.location[0].name

                    self.parent_container_set.add(parent_input_container)

                    # assemble each line of the Hamilton input file in the correct structure for the Hamilton
                    csv_line = [
                        parent_input_container,
                        parent_input_location,
                        output.location[0].name,
                        output_location,
                        reagent_barcodes['EPX1'],
                        self.process.udf['EPX 1 (uL)'],
                        reagent_barcodes['EPX2'],
                        self.process.udf['EPX 2 (uL)'],
                        reagent_barcodes['EPX3'],
                        self.process.udf['EPX 3 (uL)'],
                        reagent_barcodes['EPX Master Mix'],
                        self.process.udf['EPX Master Mix (uL)'],
                        reagent_barcodes['NaOH'],
                        self.process.udf['NaOH (uL)'],
                        reagent_barcodes['Tris-HCL'],
                        self.process.udf['Tris-HCL (uL)'],
                        reagent_barcodes['PhiX'],
                        self.process.udf['PhiX (uL)'],
                        self.process.udf['Library Volume (uL)']
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

        if self.csv_column_headers:
            csv_rows = [self.csv_column_headers]
        else:
            csv_rows = []

        counter = 0

        # create list of parent containers

        for container in sorted(self.parent_container_set):
            for column in self.plate_columns:
                for row in self.plate_rows:
                    if container + row + ":" + column in csv_dict.keys():
                        csv_rows.append(csv_dict[container + row + ":" + column])
                        counter += 1

        if counter == 0:
            raise InvalidStepError("No valid keys present in csv_dict. Key format must be row:column e.g. A:1.")

        return csv_rows


if __name__ == '__main__':
    sys.exit(GenerateHamiltonInputMakeCST().run())
