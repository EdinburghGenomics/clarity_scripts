#!/usr/bin/env python
import sys

from EPPs.common import StepEPP

#Script for performing autoplacement of samples. Loops through all inputs and assigns them to the next available space
#by column-row in the output plate
class AutoplacementMakeCFP(StepEPP):
    _use_load_config = False  # prevent the loading of the config

    def __init__(self, argv=None):
        super().__init__(argv)

    def _run(self):

        all_inputs = self.process.all_inputs(unique=True)
        if len(all_inputs) > 24:
            print("Maximum number of inputs is 24. %s inputs present in step" % (len(all_inputs)))
            sys.exit(1)

        #assemble the plate layout of the output plate as a list
        plate_layout_rows = ["1", "2", "3"]
        plate_layout_columns = ["A", "B", "C", "D", "E", "F", "G", "H"]
        plate_layout = []

        for row in plate_layout_rows:
            for column in plate_layout_columns:
                plate_layout.append(column + ":" + row)



        # update of container requires list variable containing the containers, only one container will be present in step
        # because the container has not yet been fully populated then it must be obtained from the step rather than output
        output_container_list = self.process.step.placements.get_selected_containers()
        #need a list of tuples for set_placements
        output_placement = []

        #loop through the inputs, obtain their output analytes and assign the next available position in the plate layout list
        well_counter = 0
        for input in all_inputs:
            #obtain outputs for the input that are analytes, assume step is not configured to allow replicates
            #so will always work with output[0]
            output = self.process.outputs_per_input(input.id, Analyte=True)
            #populate list of tuples for set_placements
            output_placement.append((output[0], (output_container_list[0], plate_layout[well_counter])))
            output[0].location = plate_layout[well_counter]
            well_counter += 1

        #push the output locations to the LIMS
        self.process.step.set_placements(output_container_list, output_placement)


if __name__ == '__main__':
    AutoplacementMakeCFP().run()
