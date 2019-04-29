#!/usr/bin/env python
import re
import sys

from EPPs.common import GenerateHamiltonInputEPP, InvalidStepError


class GenerateHamiltonInputQPCRDilution(GenerateHamiltonInputEPP):
    # define the column headers that will be used in the Hamilton input file and add to the csv_array to be
    # used to write the file
    csv_column_headers = ['Input Plate', 'Input Well', 'Output Plate', 'Output Well', 'Sample Volume', 'Buffer Barcode',
                          'Buffer Volume']

    # Define the output file
    output_file_name = 'QPCR DILUTION.csv'

    # Define the number of input containers that are permitted
    _max_nb_input_containers = 1

    # Define the number of output containers that are permitted
    _max_nb_output_containers = 1

    def calculate_rsb_volume(self, input_art):
        """
        The purpose of this function is to calculate the required volume of buffer to be added to a set volume of a DCT sample
        to achieve a target concentration. The dilution will only occur if the DCT sample concentration is above a threshold
         concentration. The script will also populate the output udfs of the step with a number input artifact udfs that
         will get overwritten when the QPCR is re-run. This means the values are permanently stored and can be retried in
          future.
        """
        output = self.process.outputs_per_input(input_art.id, ResultFile=True)[0]
        if None not in self.udf_names:
            for name in self.udf_names:
                output.udf[name] = input_art.udf[name]
        else:
            raise InvalidStepError('UDF population failed due to missing input value in %s' % self.udf_names)

        if float(input_art.udf['Adjusted Conc. (nM)']) > float(self.step_udfs['Threshold Concentration (nM)']):
            try:
                total_volume = float(self.step_udfs['DCT Volume (ul)']) * (
                        float(output.udf['Adjusted Conc. (nM)']) / float(self.step_udfs['Target Concentration (nM)']))
                output.udf['RSB Volume (ul)'] = str(int(round(total_volume - float(self.step_udfs['DCT Volume (ul)']),1)))
            except:
                raise InvalidStepError('Missing value. Check that step UDFs (Adjusted Conc. (nM) and Target '
                                       'Concentration (nM)) are populated')
        else:

            output.udf['RSB Volume (ul)'] = '0'
        self.artifacts_to_update.add(output)
        return output

    def _generate_csv_dict(self):
        # csv_dict will be a dictionary that consists of the lines to be present in the Hamilton input file.
        csv_dict = {}

        # find the lot number, i.e. barcode, of the RSB reagent.
        buffer_template = "LP[0-9]{7}-RSB"
        reagent_lots = list(self.process.step.reagent_lots)

        buffer_barcode = None
        for lot in reagent_lots:
            if re.match(buffer_template, lot.lot_number):
                buffer_barcode = lot.lot_number

        if not buffer_barcode:
            raise InvalidStepError('Please assign buffer lot before generating Hamilton input.')

        # find all the inputs for the step that are analytes (i.e. samples and not associated files)
        for input_art in self.artifacts:
            if input_art.type == 'Analyte':
                output = self.calculate_rsb_volume(input_art)

                # remove semi-colon from locations as this is not compatible with Hamilton Venus software
                input_location = input_art.location[1].replace(':', '')

                # assemble each line of the Hamilton input file in the correct structure for the Hamilton
                # in this step the barcode is transferred from the input to the output plate so no new analyte is
                # created and not output location exists. The transfer is 1:1 so therefore the input container and input
                #  location are used for both input and output locations in the hamilton input file
                csv_line = [
                    input_art.container.name, input_location, input_art.container.name, input_location,
                    self.step_udfs['DCT Volume (ul)'], buffer_barcode, output.udf['RSB Volume (ul)']
                ]
                # build a dictionary of the lines for the Hamilton input file with a key that facilitates
                # the lines being by input container then column then row
                csv_dict[input_art.location[1]] = csv_line

        return csv_dict

    def _run(self):
        # create the set to hold the inputs to be updated with the output from the calculation
        self.artifacts_to_update = set()
        #input udfs to be transposed to output udfs
        self.udf_names = ['Adjusted Conc. (nM)', 'Ave. Conc. (nM)', 'Original Conc. (nM)', '%CV']

        self.step_udfs = self.process.udf

        """Generic run that checks the number of input and output container
        then creates the two csv files ('-hamilton_input.csv' and the one on the shared drive)."""
        csv_array = self.generate_csv_array()

        """Create and write the Hamilton input file, this must have the hamilton_input argument as the prefix as
         this is used by Clarity LIMS to recognise the file and attach it to the step"""
        self.write_csv(self.hamilton_input + '-hamilton_input.csv', csv_array)
        self.write_csv(self.shared_drive_file_path, csv_array)

        # update all output artifacts with input artifact values and new RSB volumes
        self.lims.put_batch(list(self.artifacts_to_update))


if __name__ == '__main__':
    sys.exit(GenerateHamiltonInputQPCRDilution().run())
