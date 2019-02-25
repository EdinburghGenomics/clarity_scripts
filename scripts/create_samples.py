#!/usr/bin/env python

import re

from cached_property import cached_property
from pyclarity_lims.entities import Sample, Container

from EPPs.common import StepEPP, get_workflow_stage, InvalidStepError


class CreateSamples(StepEPP):
    # uses step UDF data to create all of the samples required by the Project Manager with the sample UDFs popualated
    # before created of the sample manifest for issue to the customer
    _use_load_config = False  # prevent the loading of the config
    _max_nb_project = 1
    _max_nb_input = 1

    udf_to_container_type = {
        '96 well plate': ['96 well plate'],
        'Tube': ['rack 96 positions', 'SGP rack 96 positions']
    }

    def _validate_step(self):
        """Perform checks that user is working with their required container type and has been named correctly and that
        the input sample has the correct name format"""
        # run normal validation
        super()._validate_step()

        # Check additional validation
        current_container = self.artifacts[0].container
        input_sample = self.samples[0]
        input_project = self.projects[0]
        udf_container_type = self.process.udf['Container Type']

        if current_container.type.name not in ['rack 96 positions', '96 well plate', 'SGP rack 96 positions']:
            raise InvalidStepError(
                message=current_container.type.name + ' is not a valid container type for this step.'
            )

        # Check container type
        if current_container.type.name not in self.udf_to_container_type[udf_container_type]:
            raise InvalidStepError(message='Input container is a %s but Container Type UDF is set to %s' %(
                current_container.type.name, udf_container_type
            ))

        # Check input container name
        suffix_udf_name = 'Rack Suffix'
        if udf_container_type == '96 well plate':
            suffix_udf_name = 'Plate Suffix'
        expected_container_re = input_project.name + self.process.udf[suffix_udf_name]
        print(expected_container_re, current_container.name)
        if not re.match(expected_container_re, current_container.name):
            raise InvalidStepError(message='Input container name is not valid for the container type. '
                                           'It should match: ' + expected_container_re)

        # check the sample name
        expected_sample_re = expected_container_re + 'A01'
        if not re.match(expected_sample_re, input_sample.name):
            raise InvalidStepError(message='Input sample name is not valid. It should match: ' + expected_sample_re)

    @cached_property
    def common_sample_udfs(self):
        """iterate through all step udfs and find those with tags [C] at the start"""
        return [udf for udf in self.process.udf if udf.startswith('[C]')]

    @cached_property
    def sample_udfs_groups(self):
        """iterate through all step udfs and find those with tags [G] at the start"""
        return [udf for udf in self.process.udf if udf.startswith('[G]')]

    def sample_udf_group(self, group):
        """return the sample udf of a specific group"""
        return [udf for udf in self.sample_udfs_groups if udf.endswith('(%s)' % group)]

    def _next_sample(self):

        sample_name = self.current_container.name + plate96_layout[plate96_layout_counter].replace(":", "")

    def _create_sample_dict(self, group_number):
        sample_udf_dict = {}
        # sample_name = current_container.name + plate96_layout[plate96_layout_counter].replace(":", "")

        # add common sample udfs
        for common_udf in self.common_sample_udfs:
            udf_value = str(self.process.udf.get(common_udf, '-'))
            if udf_value in ['-', '0']:
                raise InvalidStepError(message=common_udf + ' has not been populated.')
            else:
                sample_udf_dict[common_udf[3:]] = self.process.udf[common_udf]

        # add group sample udfs
        for group_udf in self.sample_udf_group(group_number):
            udf_value = str(self.process.udf.get(group_udf, '-'))
            if udf_value in ['-', '0']:
                raise InvalidStepError(group_udf + ' has not been populated.')
            else:
                sample_udf_dict[group_udf[3:-3]] = udf_value



        # sample_dict = {'container': current_container, 'project': input_project, 'name': sample_name,
        #                'position': plate96_layout[plate96_layout_counter], 'udf': sample_udf_dict}
        # return sample_dict

    def _run(self):
        input_sample = self.artifacts[0].samples[0]
        input_project = input_sample.project
        current_container = input_sample.artifact.container

        # assemble the plate layout of the 96 well plate as a list.
        plate96_layout_columns = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
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

        # the attributes of the new samples are defined in a list of dicts and then created with batch create
        samples_to_create = []
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
                #first create the dictionary of sample UDFs that will  either be used when adding the sample to the batch of
                #samples for the batch create or for updating the input sample
                if sample_counter == 0 and group_counter == 1:
                    sample_udf_dict=input_sample.udf
                else:
                    sample_udf_dict={}
                    sample_name = current_container.name + plate96_layout[
                        plate96_layout_counter].replace(":", "")

                # add common sample udfs
                for common_udf in sample_udf_common:
                    if str(self.process.udf[common_udf]) == '-' or str(self.process.udf[common_udf]) == '0':
                        raise ValueError(common_udf + ' has not been populated.')
                    else:
                        sample_udf_dict[common_udf[3:]] = self.process.udf[common_udf]

                # add group sample udfs
                for group_udf in sample_udf_group:
                    if str(self.process.udf[group_udf + '(' + str(group_counter) + ')']) == '-' or \
                            str(self.process.udf[group_udf + '(' + str(group_counter) + ')']) == '0':
                        raise ValueError(group_udf + ' has not been populated.')
                    else:
                        sample_udf_dict[group_udf[3:]] = self.process.udf[group_udf + '(' + str(group_counter) + ')']


                if sample_counter == 0 and group_counter == 1:
                    input_sample.put()

                else:
                    sample_dict={'container': current_container,'project': input_project, 'name': sample_name,
                                 'position':plate96_layout[plate96_layout_counter],'udf': sample_udf_dict}
                    samples_to_create.append(sample_dict)



                sample_counter += 1
                plate96_layout_counter += 1

                if plate96_layout_counter % 96 == 0:
                    current_container_name = self.find_available_container(input_project.name, current_container.type.name)
                    print(current_container_name)
                    current_container = Container.create(self.lims, type=current_container.type, name=current_container_name)
                    current_container.put()

                    plate96_layout_counter = 0

            group_counter += 1
            sample_counter = 0

        #create any new samples
        if samples_to_create:
            samples=self.lims.create_batch(Sample, samples_to_create)
            self.lims.get_batch(samples,force=True)


            # Assign any newly created samples to the create manifest step
            for sample in samples:
                sample_artifacts.append(sample.artifact)



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
