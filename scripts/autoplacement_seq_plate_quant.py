#!/usr/bin/env python
import sys

from EPPs.common import StepEPP, InvalidStepError


# Script for performing autoplacement of samples for the Sequencing Plate Quantification step. Places standards SDNA Std A1 to H1
# with 3 replicates in the first 3 columns (1 set of replicates per column). The remaining columns are filled with between 1 to 24
# samples with 3 replicates. Replicates are placed across columns to allow for maximum efficiency when multiple samples taken from a
# single input plate.

class AutoplacementSeqPlateQuant(StepEPP):
    _use_load_config = False  # prevent the loading of the config

    def _run(self):


        # loop through the inputs, assemble a nested dictionary {containers:{input.location:output} this can then be
        # queried in the order container-row-column so the order of the inputs in the Hamilton input file is
        # as efficient as possible.
        standards_dict = {}
        outputs_dict = {}

        # update of container requires list variable containing the containers, only one container will be present in step
        # because the container has not yet been fully populated then it must be obtained from the step rather than output
        output_container_list = self.process.step.placements.get_selected_containers()

        len_all_inputs_unique= len(self.process.all_inputs(unique=True))
        if len_all_inputs_unique > 32:
            raise InvalidStepError(message="Maximum number of inputs is 32. %s inputs present in step" % (len_all_inputs_unique))

        for art in self.process.all_inputs(unique=True):

            # obtain list outputs for the inputs. Sort list in case each output replicate has a unique name based on the replicate number e.g. sampleAreplicate-1, sampleAreplicate-2
            outputs = sorted(self.process.outputs_per_input(art.id,ResultFile=True), key=lambda x: x.name, reverse=False)

            if len(outputs) != 3:
                raise InvalidStepError(
                    message="3 replicates required for each sample and standard. Did you remember to click 'Apply' when assigning replicates?")

            # assemble dict of standards and dictionary of output artifacts
            #  We want to pipette the standards into the first 3 columns using all 8 channels so build the key using the replicate number and then the name.
            #  We want to be able to pipette the samples as efficiently as possible so build their key with replicate number, container name, then column then row which
            #   means if sorted alphanumerically they will sort into columns within containers

            if art.name.split(" ")[0] == "SDNA":
                output_counter = 0
                for output in outputs:
                    standards_dict[str(output_counter) + str(art.name)] = output
                    output_counter += 1

            else:
                output_counter = 0
                for output in outputs:
                    outputs_dict[str(output_counter) + art.container.name + art.location[1][2:] + art.location[1][
                        0]] = output
                    output_counter += 1

        #length of standards_dict is 3 x number of standards in step (i.e. 3 replicates each). Must equal 24 if
        #all standards have been added correctly.
        if len(standards_dict) != 24:
            raise InvalidStepError(
                message="Standards missing from step. All 8 standards should be added to the step.")

        # assemble the plate layout of the output plate with the 8 standards stamped across the first 3 columns
        # and each set of sample replicates stamped across three neighbouring columns
        plate_layout_rows = ["A", "B", "C", "D", "E", "F", "G", "H"]

        plate_layout_columns = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]

        plate_layout = []

        # layout of standards
        for column in plate_layout_columns:
            for row in plate_layout_rows:
                plate_layout.append(row + ":" + column)

        # layout of samples columns 4,5 and 6
        for row in plate_layout_rows:
            for column in plate_layout_columns[3:5]:
                plate_layout.append(row + ":" + column)

        # layout of samples columns 7,8 and 9
        for row in plate_layout_rows:
            for column in plate_layout_columns[6:8]:
                plate_layout.append(row + ":" + column)

        # layout of samples columns 10,11 and 12
        for row in plate_layout_rows:
            for column in plate_layout_columns[9:11]:
                plate_layout.append(row + ":" + column)

        well_counter = 0

        # create the output_placement_list to be used by the set_placements function

        output_placement_list = []

        # loop through sorted standards dict and add to output_placement_list
        for key in sorted(standards_dict.keys()):

            output_placement_list.append(
                (standards_dict[key], (output_container_list[0], plate_layout[well_counter])))

            well_counter += 1



        # loop through samples dict and add to output_placement_list. Add rules to ensure that replicates are always
        # stamped across three columns to permit maximum simultaneous pipetting.
        row_counter = 1
        total_input_samples = len_all_inputs_unique - 8




        for key in sorted(outputs_dict.keys()):

            output_placement_list.append(
                (outputs_dict[key], (output_container_list[0], plate_layout[well_counter])))

            if total_input_samples > 16 and total_input_samples < 24:

                if row_counter == total_input_samples:
                    well_counter = well_counter + (25 - total_input_samples)
                    row_counter = 1
                else:
                    well_counter += 1
                    row_counter += 1

            elif total_input_samples > 8 and total_input_samples < 16:

                if row_counter == total_input_samples:
                    well_counter = well_counter + (17 - total_input_samples)
                    row_counter = 1
                else:
                    well_counter += 1
                    row_counter += 1

            elif total_input_samples < 8:

                if row_counter == total_input_samples:
                    well_counter = well_counter + (9 - total_input_samples)
                    row_counter = 1
                else:
                    row_counter += 1
                    well_counter += 1

            else:
                well_counter += 1
                row_counter += 1


        # push the output locations to the LIMS
        self.process.step.set_placements(output_container_list, output_placement_list)


if __name__ == '__main__':
    sys.exit(AutoplacementSeqPlateQuant().run())