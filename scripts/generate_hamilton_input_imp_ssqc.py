#!/usr/bin/env python
import re
import sys

from EPPs.common import GenerateHamiltonInputEPP, InvalidStepError


class GenerateHamiltonInputIMPSSQC(GenerateHamiltonInputEPP):
    """"Generate a CSV containing the necessary information to transfer the fragmented sample from a covaris plate into
    an IMP plate"""
    _use_load_config = False  # prevent the loading of the config
    # Define the column headers that will be used in the Hamilton input file
    csv_column_headers = ['Input Plate', 'Input Well', 'Output IMP Plate', 'Output IMP Well', 'CFP to IMP Volume',
                          'Output SSQC Plate', 'Output SSQC Well', 'CFP to SSQC Volume', 'RSB Barcode',
                          'RSB to SSQC Volume']

    # Define the output file
    output_file_name = 'KAPA_CFP_TO_IMP_AND_SSQC.csv'

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

        # find the lot number, i.e. barcode, of the RSB reagent.
        RSB_template = "LP[0-9]{7}-RSB"
        reagent_lots = list(self.process.step.reagent_lots)

        rsb_barcode = None
        for lot in reagent_lots:
            if re.match(RSB_template, lot.lot_number):
                rsb_barcode = lot.lot_number

        if not rsb_barcode:
            raise InvalidStepError(message='Please assign RSB lot before generating Hamilton input.')

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
                # outputs appear through API in random order. Build a dictionary to contain the IMP plate name and location
                # and the SSQC plate name and location
                # prepare a template list so that the first position in the list can have IMP and the second position have SSQC
                output_dict = {'IMP': [],
                               'SSQC': []
                               }

                for output in outputs:
                    if output.location[0].name.split("-")[1] == "IMP":
                        output_dict['IMP'].append(output.location[0].name)
                        output_dict['IMP'].append(output.location[1].replace(':', ''))

                    if output.location[0].name.split("-")[1] == "SSQC":
                        output_dict['SSQC'].append(output.location[0].name)
                        output_dict['SSQC'].append(output.location[1].replace(':', ''))

                # assemble each line of the Hamilton input file in the correct structure for the Hamilton

                csv_line = [input_art.container.name, input_location, output_dict['IMP'][0], output_dict['IMP'][1],
                            cfp_imp_volume, output_dict['SSQC'][0], output_dict['SSQC'][1], cfp_SSQC_volume,
                            rsb_barcode, rsb_ssqc_volume]

                # build a dictionary of the lines for the Hamilton input file with a key that facilitates the lines being
                # by input container then column then row
                csv_dict[input_art.location[1]] = csv_line

        return csv_dict


if __name__ == '__main__':
    sys.exit(GenerateHamiltonInputIMPSSQC().run())
