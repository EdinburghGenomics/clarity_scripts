#!/usr/bin/env python

from EPPs.common import StepEPP
from pyclarity_lims.entities import Sample, Container


class CreateSamples(StepEPP):
    #uses step UDF data to create all of the samples required by the Project Manager with the sample UDFs popualated
    #before created of the sample manifest for issue to the customer
    _use_load_config = False  # prevent the loading of the config

    def _run(self):

        input_sample = self.process.all_inputs(unique=True)[0].samples[0]
        input_project = input_sample.project
        current_container=input_sample.artifact.container

        udf_container_type = self.process.udf['Container Type']

        if current_container.type.name == 'rack 96 positions' and udf_container_type == '96 Well Plate':
            raise ValueError ('Input container is a rack but Container Type UDF is set to 96 Well Plate')

        if current_container.type.name == '96 well plate' and udf_container_type == 'Tube':
            raise ValueError ('Input container is a 96 Well Plate but Container Type UDF is set to Tube')

        # assemble the plate layout of the 96 well plate as a list.
        plate96_layout_columns = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
        plate96_layout_rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        plate96_layout = []

        for column in plate96_layout_columns:
            for row in plate96_layout_rows:
                plate96_layout.append(row + ":" + column)

        #plate96_layout_counter used for counting through the available positions in the plate
        plate96_layout_counter=0

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

        #sample_counter used for counting the number of samples added for each group of UDFS
        sample_counter = 0

        # the UDFs of the newly created samples are updated by a batch put (although all samples are created individually)
        samples_to_update = []

        # loop through the groups 1 to 4 (if present in the step) and create the corresponding samples which the correct
        # sample UDF values pulled from the group step UDFS
        while group_counter <= number_of_groups:
            while sample_counter < self.process.udf['Number in Group ' + str(group_counter)]:

                if sample_counter == 0 and group_counter == 1:
                    sample=input_sample

                else:
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

                sample_counter += 1
                plate96_layout_counter += 1

                if plate96_layout_counter % 96 == 0:

                    current_container = Container.create(self.lims,
                                                        type=current_container.type)
                    current_container.name = self.find_available_container(input_project.name,current_container.type.name)
                    current_container.put()

                    plate96_layout_counter = 0

            group_counter += 1
            sample_counter = 0

        self.lims.put_batch(samples_to_update)


if __name__ == "__main__":
    CreateSamples().run()
