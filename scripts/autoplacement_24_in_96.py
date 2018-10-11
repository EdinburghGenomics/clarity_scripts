#!/usr/bin/env python
import sys

from EPPs.common import StepEPP

#Script for performing autoplacement of samples. If 1 input and 1 output then 1:1 placement. If multiple input plates then
#takes all samples from each plate before next plate Loops through all inputs and assigns them to the next available space
#by column-row in the output plate
class Autoplacement24in96(StepEPP):
    _use_load_config = False  # prevent the loading of the config

    def __init__(self, argv=None):
        super().__init__(argv)

    def _run(self):

        all_inputs = self.process.all_inputs(unique=True)
        if len(all_inputs) > 24:
            print("Maximum number of inputs is 24. %s inputs present in step" % (len(all_inputs)))
            sys.exit(1)

        #loop through the inputs, assemble a nested dicitonary {containers:{input.location:output} this can then be
        #queried in the order container-row-column so the order of the inputs in the Hamilton input file is
        # as efficient as possible.
        input_container_nested_dict={}

        for input in all_inputs:
            #obtain outputs for the input that are analytes, assume step is not configured to allow replicates
            #so will always work with output[0]
            output = self.process.outputs_per_input(input.id, Analyte=True)[0]
            #assemble single entry dict with input location and the output from that input
            input_location_output_dict = {input.location:output}
            #add the input_location_output_dict to the input_container_nested dict
            if input.container not in input_container_nested_dict.keys():
                input_container_nested_dict[input.container]={}
            #note that .location returns a tuple with the container entity and the well location as the string in position [1]
            input_container_nested_dict[input.container][input.location[1]] = output


        # update of container requires list variable containing the containers, only one container will be present in step
        # because the container has not yet been fully populated then it must be obtained from the step rather than output
        output_container_list = self.process.step.placements.get_selected_containers()
        #need a list of tuples for set_placements
        output_placement = []

        #assemble the plate layout of the output plate as a list
        plate_layout_columns = ["1", "2", "3"]
        plate_layout_rows = ["A", "B", "C", "D", "E", "F", "G", "H"]
        plate_layout = []

        for column in plate_layout_columns:
            for row in plate_layout_rows:
                plate_layout.append(row + ":" + column)

        #create a counter so only use each available well in the output plate once (24 wells available in the 96 well plate
        well_counter = 0

        #loop through the input containers and place the samples in row-column order - this makes pipetting as efficient
        #as possible, particularly if only 1 input plate so 1:1 pipetting
        for container in input_container_nested_dict:
            for column in plate_layout_columns:
                for row in plate_layout_rows:
                    # populate list of tuples for set_placements if well exists in input plate
                    if row+":"+column in input_container_nested_dict[container].keys():
                        output_placement.append((input_container_nested_dict[container][row+":"+column],
                                              (output_container_list[0], plate_layout[well_counter])))
                        well_counter += 1

        #push the output locations to the LIMS
        self.process.step.set_placements(output_container_list, output_placement)


if __name__ == '__main__':
    Autoplacement24in96().run()
