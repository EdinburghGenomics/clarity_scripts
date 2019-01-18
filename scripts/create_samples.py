#!/usr/bin/env python

from EPPs.common import StepEPP
from pyclarity_lims.entities import Sample, Container


# 96 well plates can be created in two different occasions within the script
def create_96_well_plate(self, project_name,container_type):
    output_container = Container.create(self.lims, type=self.lims.get_container_types(name='96 well plate')[0])
    output_container.name = self.find_available_container(project_name, container_type)
    output_container.put()
    return output_container


class CreateSamples(StepEPP):
    _use_load_config = False  # prevent the loading of the config

    def _run(self):

        input_sample = self.process.all_inputs(unique=True)[0].samples[0]
        input_project = input_sample.project

        udf_container_type = self.process.udf['Container Type']

        # assemble the plate layout of the output 96 well imp output plate as a list. The rows and columns are also used for looping through the output_dict
        plate96_layout_columns = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
        plate96_layout_rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        plate96_layout = []

        for column in plate96_layout_columns:
            for row in plate96_layout_rows:
                plate96_layout.append(row + ":" + column)

        # find the number of groups that have been populated in the step with the assumption that the maximum possible
        # is 4
        number_of_groups = 0
        group_counter = 1

        while group_counter <= 4:
            if self.process.udf['Number in Group ' + str(group_counter)] > 0:
                number_of_groups += 1
            group_counter += 1

        # reset group counter to 1 as this is used to count through the creation of samples in the differentr groups
        group_counter = 1

        # if the input sample should be updated then this informaiton is pulled from the first group
        if self.process.udf['Populate input sample?'] == 'Yes':
            # populate udfs in input sample
            input_sample.udf['Coverage (X)'] = self.process.udf['Coverage (X) (1)']
            input_sample.udf['Species'] = self.process.udf['Species (1)']
            input_sample.udf['Genome Version'] = self.process.udf['Genome Version (1)']
            input_sample.udf['Prep Workflow'] = self.process.udf['Library Type']
            input_sample.udf['Delivery'] = self.process.udf['fastqMerged or Split?']
            input_sample.udf['Analysis Type'] = self.process.udf['Analysis Type']
            input_sample.udf['User Prepared Library'] = self.process.udf['User Prepared Library']
            input_sample.put()

        if self.process.udf['Add new samples to input container?'] == 'Yes':
            # the first sample already exists so start filling the plate from B:1
            plate96_layout_counter = 1
            current_container = self.process.all_inputs(unique=True)[0].container

        elif self.process.udf['Add new samples to input container?'] == 'No':
            plate96_layout_counter = 0
            current_container = create_96_well_plate(self, input_project.name, '96 well plate')

        # sample counter is intially set to 1 as the input sample is populated in the scripting above not in the while
        # loop
        sample_counter = 1

        # the UDFs of the newly created samples are updated by a batch put (although all samples are created individually)
        samples_to_update = []

        # loop through the groups 1 to 4 (if present in the step) and create the corresponding samples which the correct
        # sample UDF values pulled from the group step UDFS
        while group_counter <= number_of_groups:

            while sample_counter < self.process.udf['Number in Group ' + str(group_counter)]:
                sample_name = input_project.name + current_container.name + plate96_layout[
                    plate96_layout_counter].replace(":", "")
                sample = Sample.create(self.lims, container=current_container,
                                       position=plate96_layout[plate96_layout_counter],
                                       name=sample_name, project=input_project)

                sample.udf['Coverage (X)'] = self.process.udf['Coverage (X) (' + str(group_counter) + ')']
                sample.udf['Species'] = self.process.udf['Species (' + str(group_counter) + ')']
                sample.udf['Genome Version'] = self.process.udf['Genome Version (' + str(group_counter) + ')']
                sample.udf['Prep Workflow'] = self.process.udf['Library Type']
                sample.udf['Delivery'] = self.process.udf['fastqMerged or Split?']
                sample.udf['Analysis Type'] = self.process.udf['Analysis Type']
                sample.udf['User Prepared Library'] = self.process.udf['User Prepared Library']

                samples_to_update.append(sample)
                print
                sample_counter += 1
                plate96_layout_counter += 1

                if plate96_layout_counter % 96 == 0:
                    current_container = create_96_well_plate(input_project.name, udf_container_type)

                    plate96_layout_counter = 0

            group_counter += 1
            sample_counter = 0

        self.lims.put_batch(samples_to_update)


if __name__ == "__main__":
    CreateSamples().run()
