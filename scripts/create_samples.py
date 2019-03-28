#!/usr/bin/env python

import re
from itertools import product

from cached_property import cached_property
from pyclarity_lims.entities import Sample, Container

from EPPs.common import StepEPP, get_workflow_stage, InvalidStepError, RestCommunicationEPP


class CreateSamples(StepEPP, RestCommunicationEPP):
    """uses step UDF data to create all of the samples required by the Project Manager with the sample UDFs populated
    before created of the sample manifest for issue to the customer."""
    _use_load_config = False  # prevent the loading of the config
    _max_nb_project = 1
    _max_nb_input = 1

    # mapping used to link udf value to the container type
    udf_to_container_type = {
        '96 well plate': ['96 well plate'],
        'Tube': ['rack 96 positions', 'SGP rack 96 positions']
    }
    plate96_layout_counter = 0
    plate96_layout = list(product([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']))
    current_container = None

    def _validate_step(self):
        """Perform checks to ensure the step has been setup properly. It inlcudes the normal validation and:
          - check for required container type and name format
          - check for input sample name format
          - check that next step exists
          - check that the common step UDFs are populated.
          - check that the group step UDFs are populated when the group is in use.
          - Check that the species and genome version exist in the REST API."""
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
            raise InvalidStepError(message='Input container is a %s but Container Type UDF is set to %s' % (
                current_container.type.name, udf_container_type
            ))

        # Check input container name format is as expected
        suffix_udf_name = 'Rack Suffix'
        if udf_container_type == '96 well plate':
            suffix_udf_name = 'Plate Suffix'
        expected_container_re = input_project.name + self.process.udf[suffix_udf_name]
        if not re.fullmatch(expected_container_re, current_container.name):
            raise InvalidStepError(message='Input container name is not valid for the container type. '
                                           'It should match: ' + expected_container_re)

        # check the sample name format is as expected
        expected_sample_re = expected_container_re + 'A01'
        if not re.match(expected_sample_re, input_sample.name):
            raise InvalidStepError(message='Input sample name is not valid. It should match: ' + expected_sample_re)

        # Check that the workflow stage exists
        if not self.next_stage:
            raise InvalidStepError(
                message='Stage specified by workflow: %s and stage: %s does not exist in %s' % (
                    self.process.udf['Next Workflow'], self.process.udf['Next Step'], self.baseuri
                )
            )

        # Check common sample udfs are present
        for common_udf in self.common_sample_udfs:
            udf_value = str(self.process.udf.get(common_udf, '-'))
            if udf_value in ['-', '0']:
                raise InvalidStepError(message=common_udf + ' has not been populated.')

        # Check group sample udfs are present if group is present
        # Also validate UDFs value against the REST API
        for group_number in range(1, 5):
            if self.process.udf.get('Number in Group ' + str(group_number)) > 0:
                for group_udf in self.sample_udfs_group(group_number):
                    udf_value = str(self.process.udf.get(group_udf))
                    if udf_value in ['-', '0']:
                        raise InvalidStepError(group_udf + ' has not been populated.')
                    elif 'Species' in group_udf and not self.validate_species(udf_value):
                        raise InvalidStepError(udf_value + ' in ' + group_udf + 'is not a valid species')
                    elif 'Genome Version' in group_udf and not self.validate_genome_version(udf_value):
                        raise InvalidStepError(udf_value + ' in ' + group_udf + 'is not a valid genome version')

    def validate_species(self, species_name):
        """Validate species name against REST API."""
        if self.get_documents('species', where={'name': species_name}):
            return True
        return False

    def validate_genome_version(self, genome_version):
        """Validate genome version against REST API unless it is empty."""
        if genome_version == '' or self.get_documents('genomes', where={'assembly_name': genome_version}):
            return True
        return False

    @cached_property
    def common_sample_udfs(self):
        """iterate through all step udfs and find those with tags [C] at the start"""
        return [udf for udf in self.process.udf if udf.startswith('[C]')]

    @cached_property
    def sample_udfs_groups(self):
        """iterate through all step udfs and find those with tags [G] at the start"""
        return [udf for udf in self.process.udf if udf.startswith('[G]')]

    def sample_udfs_group(self, group):
        """return the sample udf of a specific group"""
        return [udf for udf in self.sample_udfs_groups if udf.endswith('(%s)' % group)]

    @cached_property
    def next_stage(self):
        return get_workflow_stage(self.lims, self.process.udf['Next Workflow'], self.process.udf['Next Step'])

    def _next_sample_name_and_pos(self):
        """Provide the next available position on the current container and generate the associated sample name.
        When the container runs out of positions, create a new container and start again."""
        if not self.current_container:
            self.current_container = self.artifacts[0].container
        elif self.plate96_layout_counter >= 96:
            self.current_container = Container.create(
                self.lims,
                type=self.current_container.type,
                name=self.find_available_container(self.projects[0].name, self.current_container.type.name)
            )
            self.plate96_layout_counter = 0
        r, c = self.plate96_layout[self.plate96_layout_counter]
        sample_name = self.current_container.name + '%s%02d' % (c, r)
        self.plate96_layout_counter += 1
        return sample_name, '%s:%d' % (c, r)

    def _create_sample_dict(self, group_number):
        """Create the sample dictionary as required for create_batch function.
        It uses the step udf of the specified group to populate the sample udfs."""
        sample_udf_dict = {}
        # add common sample udfs
        for common_udf in self.common_sample_udfs:
            sample_udf_dict[common_udf[3:]] = self.process.udf[common_udf]

        # add group sample udfs
        for group_udf in self.sample_udfs_group(group_number):
            sample_udf_dict[group_udf[3:-3]] = self.process.udf.get(group_udf)

        sample_name, sample_position = self._next_sample_name_and_pos()
        return {'container': self.current_container, 'project': self.projects[0], 'name': sample_name,
                'position': sample_position, 'udf': sample_udf_dict}

    def _run(self):
        input_sample = self.samples[0]
        # update the first sample with the appropriate UDFs
        input_sample.udf = self._create_sample_dict(group_number=1).get('udf')
        input_sample.put()

        # remove one sample from the first group.
        # This won't show on the LIMS.
        self.process.udf['Number in Group 1'] -= 1
        samples_to_create = []
        for group_counter in range(1, 5):
            nb_samples_in_group = self.process.udf.get('Number in Group ' + str(group_counter))
            if nb_samples_in_group > 0:
                for i in range(nb_samples_in_group):
                    samples_to_create.append(self._create_sample_dict(group_counter))

        # Create any new samples
        if samples_to_create:
            samples = self.lims.create_batch(Sample, samples_to_create)
            self.lims.get_batch(samples, force=True)

            # Assign any newly created samples to the create manifest step
            sample_artifacts = [s.artifact for s in samples]
            self.lims.route_artifacts(sample_artifacts, stage_uri=self.next_stage.uri)


if __name__ == "__main__":
    CreateSamples().run()
