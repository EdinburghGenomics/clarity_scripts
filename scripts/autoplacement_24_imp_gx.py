#!/usr/bin/env python
import sys

from pyclarity_lims.entities import Container

from EPPs.common import StepEPP


class Autoplacement24IMPGX(StepEPP):
    """
    Script for performing autoplacement of up to 24 samples into a 96 well plate (1:1 placement)
    and a 384 well plate with a corehead stamp pattern (i.e. one corner of four wells).
    """
    _use_load_config = False  # prevent the loading of the config
    _max_nb_input_containers = 1  # only 1 input container
    _nb_analytes_per_input = 2  # Each input needs 2 output
    _max_nb_inputs = 24  # Maximum number of input in this step 24

    def _run(self):

        # the step can only be configured to have one output plate of one container type e.g. 1 x 96 well plate,
        # when it starts. Need to create a new container for the 384 gx plate then append it to the list of containers
        # in the plate.
        container_384 = Container.create(self.lims, type=self.lims.get_container_types(name="384 well plate")[0])
        self.process.step.placements.selected_containers.append(container_384)
        output_containers = self.process.step.placements.selected_containers

        # need to assemble one dictionary with the output artifacts as values and input well location as the key
        output_dict = {}
        for artifact in self.artifacts:
            # 2 replicates per input are required. 1 for the imp plate and 1 for the gx plate
            outputs = self.process.outputs_per_input(artifact.id, Analyte=True)
            output_dict[artifact.location[1]] = [outputs[0], outputs[1]]

        # assemble the plate layout of the 384 well gx output plate as a list.
        # To follow the existing GX procedure the samples should mimic a core head stamp
        plate384_layout_columns = ["1", "3", "5", ]
        plate384_layout_rows = ["A", "C", "E", "G", "I", "K", "M", "O"]
        plate384_layout = []

        for column in plate384_layout_columns:
            for row in plate384_layout_rows:
                plate384_layout.append(row + ":" + column)

        # assemble the plate layout of the output 96 well imp output plate as a list.
        # The rows and columns are also used for looping through the output_dict
        plate96_layout_columns = ["1", "2", "3"]
        plate96_layout_rows = ["A", "B", "C", "D", "E", "F", "G", "H"]
        plate96_layout = []

        for column in plate96_layout_columns:
            for row in plate96_layout_rows:
                plate96_layout.append(row + ":" + column)

        # create the output_placement_list to be used by the set_placements function
        output_placement_list = []

        # reset well counter to start for samples
        well_counter = 0

        # loop through the outputs_dict in row-column order and assign them the correct well location in
        # the output_placement_list.
        for column in plate96_layout_columns:
            for row in plate96_layout_rows:
                # build the list of tuples required for the placement function. Checking that key exists in dict where
                # the key consists of replicate number+row:column.
                if row + ":" + column in output_dict.keys():
                    output_placement_list.append((output_dict[row + ":" + column][0],
                                                  (output_containers[0], plate96_layout[well_counter])))
                    output_placement_list.append((output_dict[row + ":" + column][1],
                                                  (output_containers[1], plate384_layout[well_counter])))
                    well_counter += 1

        # push the output locations to the LIMS
        self.process.step.set_placements(output_containers, output_placement_list)


if __name__ == '__main__':
    sys.exit(Autoplacement24IMPGX().run())
