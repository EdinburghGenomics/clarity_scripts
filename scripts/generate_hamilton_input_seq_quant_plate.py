#!/usr/bin/env python
import re
import sys

from EPPs.common import GenerateHamiltonInputEPP, InvalidStepError


class GenerateHamiltonInputSeqQuantPlate(GenerateHamiltonInputEPP):
    """"Generate a CSV containing the necessary information for preparing the spectramax picogreen plate. The standards locaiton is not stored in the LIMS and will be hard-coded into the
    Hamilton method"""
    _use_load_config = False  # prevent the loading of the config
    # Define the column headers that will be used in the Hamilton input file
    csv_column_headers = ['Sample ID', 'Source Plate BC', 'Source Plate Position', 'Sample Volume (ul)',
                          'Destination Plate BC', 'Destination Plate Position', 'Master Mix Volume (ul)']
    # Define the output file
    output_file_name = 'SEQ_PLATE_QUANT.csv'

    # Define the number of input containers that are permitted
    _max_nb_input_containers = 1

    # Define the number of output containers that are permitted
    _max_nb_output_containers = 1

    def _generate_csv_dict(self):
        # build a dictionary of the csv lines with the output well as the key so can be populated into the output file in the best order for straightforward import into the Hamilton method
        # in a pattern for most efficient pipetting i.e. columns then rows
        csv_dict = {}

        # find the corresponding lot number i.e. barcode for the SDNA plate.
        sdna_template = "LP[0-9]{7}-SDNA"

        sdna_barcode = ""

        reagent_lots = list(self.process.step.reagent_lots)

        for lot in reagent_lots:
            if re.match(sdna_template, lot.lot_number):
                sdna_barcode = lot.lot_number

        if not sdna_barcode:
            raise InvalidStepError(
                message='SDNA Plate lot not selected. Please select in "Reagent Lot Tracking" at top of step.')

        # find all the inputs for the step that are analytes (i.e. samples and not associated files)
        for art in self.process.all_inputs(unique=True):

            outputs = self.process.outputs_per_input(art.id, ResultFile=True)

            # the step requires 3 output replicates per input
            if len(outputs) != 3:
                raise InvalidStepError(
                    message="3 replicates required for each sample and standard. Did you remember to click 'Apply' when assigning replicates?")

            # obtain input and output plate names (barcode) for use in loop below
            output_plate_name = outputs[0].location[0].name

            # input container and location are not stored in the LIMS for the SDNA standards but can be extrapolated from metadata in
            # the reagent record.
            if art.name.split(" ")[0] == 'SDNA':
                input_plate_name = sdna_barcode
                input_location = art.name.split(" ")[2]
            else:
                input_plate_name = art.location[0].name
                # remove colon from input location as this is not compatible with Hamilton Venus software
                input_location = art.location[1].replace(':', '')

            for output in outputs:
                # create the csv line with key based on output location that can be sorted by column then row
                csv_dict[output.location[1]] = [output.name, input_plate_name, input_location,
                                                self.process.udf['Sample Volume (ul)'], output_plate_name,
                                                output.location[1].replace(':', ''),
                                                self.process.udf['Master Mix Volume (ul)']]

        return csv_dict


if __name__ == '__main__':
    sys.exit(GenerateHamiltonInputSeqQuantPlate().run())
