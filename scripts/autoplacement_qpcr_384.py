#!/usr/bin/env python
import sys

from EPPs.common import StepEPP


# Script for performing autoplacement of samples. If 1 input and 1 output then 1:1 placement. If multiple input plates then
# takes all samples from each plate before next plate Loops through all inputs and assigns them to the next available space
# by column-row in the output plate
class AutoplacementQPCR384(StepEPP):
    _use_load_config = False  # prevent the loading of the config

    def __init__(self, argv=None):
        super().__init__(argv)

    def _run(self):

        all_inputs = self.process.all_inputs(unique=True)

        if len(all_inputs) > 31:
            print("Maximum number of input samples and standards is 31. %s inputs present in step" % (len(all_inputs)))
            return 1

        # loop through the inputs, assemble a nested dicitonary {containers:{input.location:output} this can then be
        # queried in the order container-row-column so the order of the inputs in the Hamilton input file is
        # as efficient as possible.
        input_container_nested_dict = {}

        # update of container requires list variable containing the containers, only one container will be present in step
        # because the container has not yet been fully populated then it must be obtained from the step rather than output
        output_container_list = self.process.step.placements.get_selected_containers()

        standards_dict = {}
        outputs_dict = {}

        for input in all_inputs:

            # obtain outputs for the inputs
            outputs = self.process.outputs_per_input(input.id, ResultFile=True)
            # generate error if 3 replicates not present
            if len(outputs) != 3:
                print("3 replicates required for each sample and standard")
                return 1

            # assemble dict of standards and dictionary of output artifacts
            # using numbers 0-2 to differentiate between the three replicate outputs for each input/standard
            output_counter = 0

            if input.name.split(" ")[0] == "QSTD":

                for output in outputs:
                    standards_dict[str(input.name) + str(output_counter)] = output
                    output_counter += 1

            if input.name.split(" ")[0] == "No":

                for output in outputs:
                    # want no template controles to appear after all standards in the sorted dictionary
                    standards_dict[str("z") + str(output_counter)] = output
                    output_counter += 1

            else:
                for output in outputs:
                    outputs_dict[str(output_counter) + input.location[1]] = output
                    output_counter += 1
            # check that all standards and no template control are present


        if len(standards_dict) < 21:
            print("Step requires QSTD A to F and No Template Control with 3 replicates each")
            return 1

        # assemble the plate layout of the output plate as a list
        plate_layout_columns = ["1", "2", "3", "4", "5", "6"]
        plate_layout_rows = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P"]
        plate_layout = []

        for column in plate_layout_columns:
            for row in plate_layout_rows:
                plate_layout.append(row + ":" + column)
        well_counter = 0
        # create the output_placement_list to be used by th set_placements function

        output_placement_list = []

        # loop through sorted standards dict and add to output_placement_list
        for key in sorted(standards_dict.keys()):

            output_placement_list.append((standards_dict[key], (output_container_list[0], plate_layout[well_counter])))

            if plate_layout[well_counter][1:] == ":5":
                well_counter -= 62
            else:
                well_counter += 32

        # reset well counter to start for samples
        well_counter = 1

        # need replicate counter to help pull all outputs from dict in order of replicates then row-column order
        replicate_counter = 0

        # loop through the outputs_dict in replicate and row-column order and assign them the correct well location in
        # the output_placement_list.
        for column in plate_layout_columns:
            for row in plate_layout_rows:
                 # build the list of tuples required for the placement function. Checking that key exists in dict where
                 # the key consists of replicate number+row:column.
                    if str(replicate_counter) + row + ":" + column in outputs_dict.keys():
                        output_placement_list.append((outputs_dict["0" + row + ":" + column],
                                                      (output_container_list[0], plate_layout[well_counter])))
                        output_placement_list.append((outputs_dict["1" + row + ":" + column],
                                                      (output_container_list[0], plate_layout[well_counter + 15])))
                        output_placement_list.append((outputs_dict["2" + row + ":" + column],
                                                      (output_container_list[0], plate_layout[well_counter + 16])))

                        if plate_layout[well_counter][0] == "P":
                            well_counter += 18

                        else:
                            well_counter += 2

                    replicate_counter += 1

        # push the output locations to the LIMS
        self.process.step.set_placements(output_container_list, output_placement_list)


if __name__ == '__main__':
    sys.exit(AutoplacementQPCR384().run())
