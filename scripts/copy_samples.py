#!/usr/bin/env python
import platform
from itertools import product

from egcg_core.config import cfg
from pyclarity_lims.entities import Sample, Container, Step

from EPPs.common import StepEPP, get_workflow_stage, InvalidStepError, finish_step


class CopySamples(StepEPP):
    """Creates duplicate submitted samples with the same sample UDF values as the input samples"""
    _max_nb_project = 1

    # mapping used to link udf value to the container type
    udf_to_container_type = {
        '96 well plate': ['96 well plate'],
        'Tube': ['rack 96 positions', 'SGP rack 96 positions']
    }
    plate96_layout_counter = 0
    plate96_layout = list(product([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']))
    current_container = None

    def complete_remove_from_processing(self, stage):
        # Create new step with the routed artifacts
        s = Step.create(self.lims, protocol_step=stage.step, inputs=self.artifacts,
                        container_type_name='Tube')
        url = 'https://%s/clarity/work-complete/%s' % (platform.node(), self.process.id.split('-')[1])
        s.details.udf['Reason for removal from processing:'] = 'Failed QC. See step %s' % url
        s.details.put()

        # Move from "Record detail" window to the "Next Step"
        s.advance()

        for next_action in s.actions.next_actions:
            next_action['action'] = 'complete'
        s.actions.put()

        # Complete the step
        finish_step(s)

    def next_sample_name_and_pos(self):
        """Provide the next available position on the current container and generate the associated sample name.
        When the container runs out of positions, create a new container and start again."""
        if not self.current_container:
            try:
                self.current_container = Container.create(
                    self.lims,
                    type=self.lims.get_container_types(name=self.process.udf['Container Type'])[0],
                    name=self.find_available_container(self.projects[0].name,
                                                       container_type=self.process.udf['Container Type'])
                )
            except:
                raise InvalidStepError(
                    'Container could not be created. Check that Container Type udf has been populated')

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

    def create_samples_list(self):
        samples_to_create = []
        for input_sample in self.samples:
            new_sample_name, new_sample_position = self.next_sample_name_and_pos()
            new_sample_dict = {
                'container': self.current_container,
                'project': self.projects[0],
                'name': new_sample_name,
                'position': new_sample_position,
                'udf': {'Prep Workflow': input_sample.udf['Prep Workflow'],
                        'Coverage (X)': input_sample.udf['Coverage (X)'],
                        'Required Yield (Gb)': input_sample.udf['Required Yield (Gb)'],
                        'Delivery': input_sample.udf['Delivery'],
                        'User Prepared Library': input_sample.udf['User Prepared Library'],
                        'Analysis Type': input_sample.udf['Analysis Type'],
                        'Rapid Analysis': input_sample.udf['Rapid Analysis'],
                        'Species': input_sample.udf['Species'],
                        'Genome Version': input_sample.udf['Genome Version']}
            }

            samples_to_create.append(new_sample_dict)
        return samples_to_create

    def _run(self):

        # Create new samples
        samples = self.lims.create_batch(Sample, self.create_samples_list())
        self.lims.get_batch(samples, force=True)

        # Assign newly created samples to the create manifest step
        sample_artifacts = [s.artifact for s in samples]
        stage_wf_st = cfg.query('workflow_stage', 'container_dispatch', 'start')
        stage = get_workflow_stage(self.lims, stage_wf_st[0], stage_wf_st[1])
        self.lims.route_artifacts(sample_artifacts, stage_uri=stage.uri)

        # Assign the input samples to remove from processing step then complete the remove from processing step
        stage_wf_st = cfg.query('workflow_stage', 'remove_from_processing', 'start')
        stage = get_workflow_stage(self.lims, stage_wf_st[0], stage_wf_st[1])
        self.lims.route_artifacts(self.artifacts, stage_uri=stage.uri)
        self.complete_remove_from_processing(stage)


if __name__ == "__main__":
    CopySamples().run()
