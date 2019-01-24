#!/usr/bin/env python

import re

from pyclarity_lims.entities import Sample, Container

from EPPs.common import StepEPP, get_workflow_stage


class CreateSamples(StepEPP):
    # uses step UDF data to create all of the samples required by the Project Manager with the sample UDFs popualated
    # before created of the sample manifest for issue to the customer
    _use_load_config = False  # prevent the loading of the config

    def _run(self):

        input_sample = self.process.all_inputs(unique=True)[0].samples[0]
        input_project = input_sample.project
        current_container = input_sample.artifact.container

        udf_container_type = self.process.udf['Container Type']



        # perform checks that user is working with their required container type and has been named correctly and that
        #the input sample has the correct name format

        if not current_container.type.name == 'rack 96 positions' and not current_container.type.name == '96 well plate':
            raise ValueError(current_container.type.name + ' is not a valid container type for this step.')

        if current_container.type.name == 'rack 96 positions':
            # check if user has selected container type that matches the input sample
            if udf_container_type == '96 Well Plate':
                raise ValueError('Input container is a rack but Container Type UDF is set to 96 Well Plate')

            # check that the input container name and sample name have the correct formatting
            container_name_re = input_project.name + self.process.udf['Rack Suffix']
            input_name_re = container_name_re + 'A01'
            if re.search(container_name_re, current_container.name) == 'None':
                raise ValueError('Input container name is not valid for the container type ' +
                                 container_name_re + '.')
            if re.search(input_name_re+'A01',input_sample.name) == 'None':
                raise ValueError('Input sample name is not valid '+input_name_re)

        if current_container.type.name == '96 well plate':
            # check if user has selected container type that matches the input sample
            if udf_container_type == 'Tube':
                raise ValueError('Input container is a 96 Well Plate but Container Type UDF is set to Tube')

            # check that the input container name and sample name have the correct formatting
            container_name_re = input_project.name + self.process.udf['Plate Suffix']
            input_name_re=container_name_re+'A01'

            if re.search(container_name_re, current_container.name) == 'None':
                raise ValueError('Input container name is not valid for the container type ' + container_name_re + '.')
            if re.search(input_name_re+'A01',input_sample.name) == 'None':
                raise ValueError('Input sample name is not valid '+input_name_re)

        # assemble the plate layout of the 96 well plate as a list.
        plate96_layout_columns = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
        plate96_layout_rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        plate96_layout = []

        for column in plate96_layout_columns:
            for row in plate96_layout_rows:
                plate96_layout.append(row + ":" + column)

        # plate96_layout_counter used for counting through the available positions in the plate
        plate96_layout_counter = 0

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

        # sample_counter used for counting the number of samples added for each group of UDFS
        sample_counter = 0

        # the UDFs of the newly created samples are updated by a batch put (although all samples are created individually)
        samples_to_update = []
        # the sample artifact should be assigned to the create manifest step
        sample_artifacts = []

        # the udfs to be populated in the new samples are identified by step udfs with tags - either [C] or [G]
        # group udfs have the prefix [G] and will always have a number suffix e.g. ' (1)' or ' (2)'
        # common udfs will have the prefix [C]

        sample_udf_common = []
        sample_udf_group = []

        # iterate through all step udfs and find those with tags [C] or [G]
        for udf in self.process.udf:
            if udf[0:3] == '[C]':
                sample_udf_common.append(udf)
            elif udf[0:3] == '[G]':
                sample_udf_group.append(udf[0:-3])


        # Assumption is that we will never have more than 4 different groups of sample configuration in a project.
        # Loop through the groups 1 to 4 (if present in the step) and create the corresponding samples which the correct
        # sample UDF values pulled from the group step UDFS
        while group_counter <= number_of_groups:
            while sample_counter < self.process.udf['Number in Group ' + str(group_counter)]:

                if sample_counter == 0 and group_counter == 1:
                    sample = input_sample

                else:
                    sample_name = current_container.name + plate96_layout[
                        plate96_layout_counter].replace(":", "")
                    sample = Sample.create(self.lims, container=current_container,
                                           position=plate96_layout[plate96_layout_counter],
                                           name=sample_name, project=input_project)

                # add common sample udfs
                for common_udf in sample_udf_common:
                    if str(self.process.udf[common_udf]) == '-' or str(self.process.udf[common_udf]) == '0':
                        raise ValueError(common_udf + ' has not been populated.')
                    else:
                        sample.udf[common_udf[3:]] = self.process.udf[common_udf]

                # add group sample udfs
                for group_udf in sample_udf_group:
                    if str(self.process.udf[group_udf + '(' + str(group_counter) + ')']) == '-' or \
                            str(self.process.udf[group_udf + '(' + str(group_counter) + ')']) == '0':
                        raise ValueError(group_udf + ' has not been populated.')
                else:
                    sample.udf[group_udf[3:]] = self.process.udf[group_udf + '(' + str(group_counter) + ')']

                samples_to_update.append(sample)
                sample_artifacts.append(sample.artifact)

                sample_counter += 1
                plate96_layout_counter += 1

                if plate96_layout_counter % 96 == 0:
                    current_container = Container.create(self.lims,
                                                         type=current_container.type)
                    current_container.name = self.find_available_container(input_project.name,
                                                                           current_container.type.name)
                    current_container.put()

                    plate96_layout_counter = 0

            group_counter += 1
            sample_counter = 0

        #put the modified sample UDFs into the system
        self.lims.put_batch(samples_to_update)

        # Assign newly created samples to the create manifest step

        # Find the workflow stage
        stage = get_workflow_stage(self.lims, self.process.udf['Next Workflow'], self.process.udf['Next Step'])

        if not stage:
            raise ValueError(
                'Stage specified by workflow: %s and stage: %s does not exist in %s' % (
                    self.process.udf['Next Workflow'], self.process.udf['Next Step'], self.baseuri)
            )
        self.lims.route_artifacts(sample_artifacts, stage_uri=stage.uri)


if __name__ == "__main__":
    CreateSamples().run()
