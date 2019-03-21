#!/usr/bin/env python
import itertools

from EPPs.common import StepEPP


# Script for performing autoplacement of samples from multiple input plates into a single output plate.
# If 1 input and 1 output then 1:1 placement. If multiple input plates then
# takes all samples from each plate before next plate Loops through all inputs and assigns them to the next available space
# by column-row in the output plate
class Autoplacement96well(StepEPP):
    _use_load_config = False  # prevent the loading of the config
    _max_nb_input_containers = 27
    # assemble the plate layout of the output plate as a list
    output_plate_layout_rows = ["A", "B", "C", "D", "E", "F", "G", "H"]
    output_plate_layout_columns = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]

    output_plate_layout = [(row + ":" + column) for column, row in
                           itertools.product(output_plate_layout_columns, output_plate_layout_rows)]

    # define the input plate(s) column and rows to be
    input_plate_layout_columns = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "11", "12"]
    input_plate_layout_rows = ["A", "B", "C", "D", "E", "F", "G", "H"]

    def generate_input_container_nested_dict(self):
        # loop through the inputs, assemble a nested dicitonary {containers:{input.location:output} this can then be
        # queried in the order container-row-column so the order of the inputs in the Hamilton input file is
        # as efficient as possible.
        nested_dict = {}
        for art in self.artifacts:

            # obtain outputs for the input that are analytes, assume step is not configured to allow replicates
            # so will always work with output[0]
            output = self.process.outputs_per_input(art.id, Analyte=True)[0]

            # add the input_location_output_dict to the input_container_nested dict
            if art.container not in nested_dict.keys():
                nested_dict[art.container] = {}
            # start assembling one of the variables needed to use the set_placement function
            # note that .location returns a tuple with the container entity and the well location as the string in position [1]
            nested_dict[art.container][art.location[1]] = output
        return nested_dict

    def generate_output_placement(self, output_container):
        placement = []
        # obtain the dictionary containing the source information
        input_container_nested_dict = self.generate_input_container_nested_dict()

        # create a counter so only use each available well in the output plate once (24 wells available in the 96 well plate
        well_counter = 0

        # loop through the input containers and place the samples in row-column order - this makes pipetting as efficient
        # as possible, particularly if only 1 input plate so 1:1 pipetting
        for container in sorted(input_container_nested_dict, key=lambda x: x.name):
            for column in self.input_plate_layout_columns:
                for row in self.input_plate_layout_rows:
                    # populate list of tuples for set_placements if well exists in input plate
                    if row + ":" + column in input_container_nested_dict[container].keys():
                        placement.append((input_container_nested_dict[container][row + ":" + column],
                                          (output_container, self.output_plate_layout[well_counter])))
                        well_counter += 1
        return placement

    def _run(self):

        # update of container requires list variable containing the containers, only one container will be present in step
        # because the container has not yet been fully populated then it must be obtained from the step rather than output
        output_container_list = self.process.step.placements.get_selected_containers()

        # need a list of tuples for set_placements
        output_placement = self.generate_output_placement(output_container_list[0])

        # push the output locations to the LIMS
        self.process.step.set_placements(output_container_list, output_placement)


if __name__ == '__main__':
    Autoplacement96well().run()
