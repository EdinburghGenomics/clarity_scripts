#!/usr/bin/env python
import csv
import sys

from EPPs.common import StepEPP, step_argparser
from operator import itemgetter


class GenerateHamiltonInputUPL(StepEPP):
    """"Generate a CSV containing the necessary information to batch up to 9 normalised sequencing plates
    into up to 3 picogreen plates. The Hamilton requires input and output plate containers and well positions from LIMS."""

    # additional argument required for the location of the Hamilton input file so def _init_ customised
    def __init__(self, step_uri, username, password, log_file, hamilton_input):
        super().__init__(step_uri, username, password, log_file)
        self.hamilton_input = hamilton_input

    def _run(self):
        # csv_dict will be a dictionary that consists of the lines to be present in the Hamilton input file. These are
        # then sorted into the correct order and added to the csv_array which is used to write the file
        csv_dict = {}
        csv_array = []

        # define the column headers that will be used in the Hamilton input file and add to the csv_array to be
        # used to write the file
        csv_column_headers = ['Sample ID', 'Source Plate BC', 'Source Plate Position', 'Destination Plate BC',
                              'Destination Plate Position']
        csv_array.append(csv_column_headers)

        # define the sets for listing the unique input and output containers
        unique_input_containers = set()
        unique_output_containers = set()

        # obtain all of the inputs for the step
        #all_inputs = self.process.all_inputs()



        # use the input_output_maps attribute of process to obtain a list of tuples where each tuple contains two
        #dictionaries, one dictionary for the input and one for the output.
        for input_output in self.process.input_output_maps:
            #use only input-output tuples where the output is PerInput i.e. a sample and not a shared file
            if input_output[1]['output-generation-type'] == 'PerInput':

                #find the input and output artifacts for use later on
                input=input_output[0]['uri']
                output=input_output[1]['uri']
                # build a list of the unique input containers for checking that no more than 9 are present due to
                # deck limit on Hamilton and for sorting the sample locations by input plate.
                unique_input_containers.add(input.container.name)
                # Build a list of unique output containers as no more than 3 plates can be present in Hamilton app
                unique_output_containers.add(output.container.name)


                #There will be one line in the Hamilton input for each output replicate. So assemble each line of
                # the Hamilton input file in the correct structure for the Hamilton
                csv_line = [output.name, input.container.name, input.location[1], output.container.name, output.location[1]]

                # build a dictionary of the lines for the Hamilton input file with a key that facilitates the lines being
                # by input container then column then row
                if input.container.name + input.location[1] in csv_dict.keys():
                    csv_dict[input.container.name + input.location[1]].append(csv_line)
                else:
                    csv_dict[input.container.name + input.location[1]] = [csv_line]

        #sort csv_dict so output replicates are in alphanumeric order for each input key so aspiration from neighbouring
        #wells is to be dispensed in neighbouring wells in the same plate
        for dict_key in csv_dict:
            #print("Before sort"+str(csv_dict[dict_key])+"\n")
            csv_dict[dict_key]=sorted(csv_dict[dict_key],key=itemgetter(0))
            #print("After sort"+str(csv_dict[dict_key]) + "\n\n")

        # check the number of input containers
        if len(unique_input_containers) > 9:
            print('Maximum number of input plates is 9. There are %s output plates in the step.' % (
                str(len(unique_input_containers))))
            sys.exit(1)
        # check the number of output containers
        if len(unique_output_containers) > 3:
            print('Maximum number of output plates is 3. There are %s output plates in the step.' % (
                str(len(unique_output_containers))))
            sys.exit(1)
        # define the rows and columns in the input plate (standard 96 well plate pattern)
        rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        columns = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']

        # add the lines to the csv_array that will be used to write the Hamilton input file
        count=0

        while count < len(unique_output_containers):

            for unique_input_container in sorted(unique_input_containers):
                for column in columns:
                    for row in rows:

                        if unique_input_container + row + ":" + column in csv_dict.keys() \
                                and len(list(csv_dict[unique_input_container + row + ":" + column])) == len(unique_output_containers):
                            #for output_well in list(csv_dict[unique_input_container + row + ":" + column]):

                            csv_array.append(csv_dict[unique_input_container + row + ":" + column][count])
                                #csv_array.append(output_well)
            count+=1


        # create and write the Hamilton input file, this must have the hamilton_input argument as the prefix as this is used by
        # Clarity LIMS to recognise the file and attach it to the step
        with open(self.hamilton_input + '-hamilton_input.csv', 'w') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerows(csv_array)
        csvFile.close()


def main():
    p = step_argparser()
    p.add_argument('-i', '--hamilton_input', type=str, required=True, help='Hamilton input file generated by LIMS')
    args = p.parse_args()

    action = GenerateHamiltonInputUPL(args.step_uri, args.username, args.password, args.log_file, args.hamilton_input)
    action.run()


if __name__ == '__main__':
    main()
