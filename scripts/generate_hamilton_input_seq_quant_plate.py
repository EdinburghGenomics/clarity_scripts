#!/usr/bin/env python
import sys


from EPPs.common import GenerateHamiltonInputEPP, InvalidStepError


class GenerateHamiltonInputSeqQuantPlate(GenerateHamiltonInputEPP):
    """"Generate a CSV containing the necessary information for preparing the spectramax picogreen plate. The standards locaiton is not stored in the LIMS and will be hard-coded into the
    Hamilton method"""
    _use_load_config = False  # prevent the loading of the config
    # Define the column headers that will be used in the Hamilton input file
    csv_column_headers = ['Sample ID', 'Source Plate BC', 'Source Plate Position','Sample Volume (ul)' 'Destination Plate BC', 'Destination Plate Position','Master Mix Volume (ul)']
    # Define the output file
    output_file_name = 'SEQ_PLATE_QUANT.csv'

    # Define the number of input containers that are permitted
    permitted_input_containers = 9

    # Define the number of output containers that are permitted
    permitted_output_containers = 1

    def _generate_csv_dict(self):
        #build a dictionary of the csv lines with the output well as the key so can be populated into the output file in the best order for straightforward import into the Hamilton method
        #in a pattern for most efficient pipetting i.e. columns then rows
        csv_dict = {}



        # assemble a dictionary that only contains PerInput outputs for each input based on input_output_maps

        input_output_maps = self.process.input_output_maps
        input_output_perinput_dict = {}

        for input_output in input_output_maps:
            input = input_output[0]['uri']

            if input_output[1]['output-generation-type'] == 'PerInput':
                if not input in input_output_perinput_dict.keys():
                    input_output_perinput_dict[input] = [input_output[1]['uri']]
                else:
                    input_output_perinput_dict[input].append(input_output[1]['uri'])


        # find all the inputs for the step that are analytes (i.e. samples and not associated files)
        for input in input_output_perinput_dict:

            outputs = input_output_perinput_dict[input]

            # the step requires 3 output replicates per input
            if len(outputs) != 3:
                raise InvalidStepError(message="3 replicates required for each sample and standard. Did you remember to click 'Apply' when assigning replicates?")


            # remove semi-colon from input location as this is not compatible with Hamilton Venus software
            input_location = input.location[1].replace(':', '')

            #obtain input and output plate names (barcode) for use in loop below
            input_plate_name=input.location[0].name
            output_plate_name=outputs[0].location[0].name

            # assemble each line of the Hamilton input file in the correct structure for the Hamilton
            for output in outputs:

                #remove semi-colon from output location in the variable as this is not compatible with Hamilton Venus software. Common.py
                #expects key to have semi-colon.
                #create the csv line with key based on output location that can be sorted by column then row
                csv_dict[output.location[1]]=[output.name,input_plate_name,input_location,self.process.udf['Sample Volume (ul)'],output_plate_name,output.location[1].replace(':', ''),self.process.udf['Master Mix Volume (ul)']]

        return csv_dict


if __name__ == '__main__':
    sys.exit(GenerateHamiltonInputSeqQuantPlate().run())
