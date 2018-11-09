#!/usr/bin/env python
import sys

from EPPs.common import StepEPP, InvalidStepError


# Script for performing autoplacement of samples for the Sequencing Plate Quantification step. Places standards SDNA Std A1 to H1
#with 3 replicates in the first 3 columns (1 set of replicates per column). The remaining columns are filled with between 1 to 24
#samples with 3 replicates. Replicates are placed across columns to allow for maximum efficiency when multiple samples taken from a
#single input plate.

class Autoplacement_seq_plate_quant(StepEPP):
    _use_load_config = False  # prevent the loading of the config

    def __init__(self, argv=None):
        super().__init__(argv)

    def _run(self):

        all_inputs = self.process.all_inputs(unique=True)
        if len(all_inputs) > 32:
            print("Maximum number of inputs is 31. %s inputs present in step" % (len(all_inputs)))
            sys.exit(1)

        # loop through the inputs, assemble a nested dictionary {containers:{input.location:output} this can then be
        # queried in the order container-row-column so the order of the inputs in the Hamilton input file is
        # as efficient as possible.
        standards_dict = {}
        outputs_dict = {}

        # update of container requires list variable containing the containers, only one container will be present in step
        # because the container has not yet been fully populated then it must be obtained from the step rather than output
        output_container_list = self.process.step.placements.get_selected_containers()

        input_output_maps=self.process.input_output_maps

        input_output_PerInput_dict={}

        for input_output in input_output_maps:
            input = input_output[0]
            if input_output[1]['output-generation-type'] == 'PerInput'
                if not input_output_PerInput_dict[input]:
                    input_output_PerInput_dict[input] = input_output[1]['uri']
                else:


            outputs = input_output[1]
            print(outputs)

        for input in all_inputs:

            # obtain outputs for the inputs
            outputs = self.process.outputs_per_input(input.id, ResultFile=True, SharedResultFile=False)
            print(len(outputs))
            if len(outputs) != 3:
                raise InvalidStepError(message="3 replicates required for each sample and standard. Did you remember to click 'Apply' when assigning replicates?")

            # assemble dict of standards and dictionary of output artifacts
            #  We want to pipette the standards in columns using all 8 channels so build there key using the replicate number and then the name. This means when the
            # dict is sorted we will get the first set of replicates for each standard, then the second then the third which is easy to assigne to the first 3 columns of the output plate.from
            # Use numbers 0-2 to differentiate between the three replicate outputs for each input/standard i.e. 1SDNA A1: replicate_artifact1, 2SDNA A1: replicate_artifact2, 3SDNA A1: replicate_artifact3,


            if input.name.split(" ")[0] == "SDNA":
                output_counter = 0
                for output in outputs:
                    standards_dict[str(output_counter)+str(input.name)] = output
                    output_counter += 1

            else:
                output_counter = 0
                for output in outputs:
                    outputs_dict[str(output_counter) + input.location[1]] = output
                    output_counter += 1

                # assemble the plate layout of the output plate as a list
                plate_layout_columns = ["1", "2", "3", "4", "5", "6","7","8","9","10","11","12"]
                plate_layout_rows = ["A", "B", "C", "D", "E", "F", "G", "H"]
                plate_layout = []

                for column in plate_layout_columns:
                    for row in plate_layout_rows:
                        plate_layout.append(row + ":" + column)
                well_counter = 0
                # create the output_placement_list to be used by the set_placements function

                output_placement_list = []

                # loop through sorted standards dict and add to output_placement_list
                for key in sorted(standards_dict.keys()):

                    output_placement_list.append(
                        (standards_dict[key], (output_container_list[0], plate_layout[well_counter])))

                    well_counter+=1

                for key in sorted(outputs_dict.keys()):
                    output_placement_list.append(
                        (outputs_dict[key], (output_container_list[0], plate_layout[well_counter])))

                    well_counter += 1


                # push the output locations to the LIMS
                self.process.step.set_placements(output_container_list, output_placement_list)



if __name__ == '__main__':
    sys.exit(Autoplacement_seq_plate_quant().run())
