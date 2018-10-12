#!/usr/bin/env python
import sys

from EPPs.common import StepEPP

#Script for performing autoplacement of samples. If 1 input and 1 output then 1:1 placement. If multiple input plates then
#takes all samples from each plate before next plate Loops through all inputs and assigns them to the next available space
#by column-row in the output plate
class AutoplacementQPCR384(StepEPP):
    _use_load_config = False  # prevent the loading of the config

    def __init__(self, argv=None):
        super().__init__(argv)

    def _run(self):

        all_inputs = self.process.all_inputs(unique=True)
        if len(all_inputs) > 31:
            print("Maximum number of input samples and standards is 31. %s inputs present in step" % (len(all_inputs)))
            sys.exit(1)

        #loop through the inputs, assemble a nested dicitonary {containers:{input.location:output} this can then be
        #queried in the order container-row-column so the order of the inputs in the Hamilton input file is
        # as efficient as possible.
        input_container_nested_dict={}

        # update of container requires list variable containing the containers, only one container will be present in step
        # because the container has not yet been fully populated then it must be obtained from the step rather than output
        output_container_list = self.process.step.placements.get_selected_containers()

        standards_dict={}
        outputs_dict={}

        for input in all_inputs:
            #obtain outputs for the input that are analytes, assume step is not configured to allow replicates
            #so will always work with output[0]
            outputs = self.process.outputs_per_input(input.id, ResultFile=True)


            #assemble dict of standards and dictionary of output artifacts
            if input.name.split(" ") == "QSTD":
                for output in outputs:
                    standards_dict[input.name]=output
            else:
                for output in outputs:
                    outputs_dict[input.location[1]]=output





        #assemble the plate layout of the output plate as a list
        plate_layout_columns = ["1", "2", "3","4","5","6"]
        plate_layout_rows = ["A", "B", "C", "D", "E", "F", "G", "H","I","J","K","L","M","N","O","P","Q","R",
                             "S","T","U","V","W","X","Y","Z"]
        plate_layout = []

        for column in plate_layout_columns:
            for row in plate_layout_rows:
                plate_layout.append(row + ":" + column)
        well_counter=0
        #create the output_placement_list to be used by th set_placements function
        output_placement_list=[]

        #loop through sorted standards dict and add to output_placement_list

        for key in standards_dict.keys().sort:
            output_placement_list.append((standards_dict[key],(output_container_list[0],plate_layout[well_counter])))
            if plate_layout[wellcounter][1:] == 5:
                well_counter-=62
            else:
                well_counter+=32

        #reset well counter to start for samples
        well_counter=2


        #loop through the outputs_dict in row-column order and assign them the correct well location in
        # the output_placement_list
        for column in columns:
            for row in rows:
                #build the list of tuples required for the placement function
                output_placement_list.append((outputs_dict[row+":"+column],(output_container_list[0],plate_layout[well_counter])))
                if plate_layout[wellcounter][0:1] == "P":
                    well_counter +=18
                if plate_layout[wellcounter] == "P5":
                    well_counter-=33
                if plate_layout[wellcounter] == "06":
                    well_counter-=35
                else:
                    well_counter += 2



        #push the output locations to the LIMS
        self.process.step.set_placements(output_container_list, output_placement)


if __name__ == '__main__':
    AutoplacementQPCR384().run()
