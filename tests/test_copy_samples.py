from builtins import sorted
from itertools import cycle
from unittest.mock import patch, Mock

import pytest
from requests import HTTPError

from pyclarity_lims.entities import Sample

from scripts.copy_samples import CopySamples
from scripts.create_samples import CreateSamples, Container
from tests.test_common import TestEPP, FakeEntitiesMaker


class TestCopySamples(TestEPP):
    mocked_step = Mock(details=Mock(udf={}), actions=Mock(next_actions=[{}]))
    patched_get_workflow_stage = patch('scripts.copy_samples.get_workflow_stage', return_value=Mock(uri='a_uri',
                                                                                                    step=mocked_step))
    patched_create_batch = patch('lims.create_samples.create_batch', return_value=True)

    @staticmethod
    def get_patch_create_container(container):
        return patch.object(Container, 'create', return_value=container)

    def setUp(self):
        self.epp = CopySamples(self.default_argv)
        self.fem_params = {
            'nb_input':2,
            'project_name': 'X99999',
            'process_id': '99-9999',
            'input_container_name': 'X99999P001',
            'sample_name': cycle(['X99999P001A01',
                                  'X99999P001B01']),
            'sample_udfs':{
                   'Prep Workflow': cycle(['TruSeq Nano DNA Sample Prep','TruSeq PCR-Free DNA Sample Prep']),
                   'Coverage (X)': cycle([30,60]),
                   'Required Yield':cycle([120,240]),
                   'Species': cycle(['Homo sapiens','Mus musculus']),
                   'Genome Version': cycle(['hg38','hg19']),
                   'Delivery': cycle(['merged','split']),
                   'Analysis Type': cycle(['Variant Calling gatk','None']),
                   'Rapid Analysis': cycle(['No','Yes']),
                   'User Prepared library':cycle(['No','Yes'])},
            'step_udfs':{'Container Type':'96 well plate'},
            'output_per_input': 0,
            'process_id':'99-9999'

            }


    def test_next_sample_name_and_pos(self):
        fem = FakeEntitiesMaker()
        self.epp.lims = fem.lims
        self.epp.process = fem.create_a_fake_process(**self.fem_params)
        self.epp.lims.get_containers = Mock(return_value=[])
        with self.get_patch_create_container(fem.create_a_fake_container(container_name='X99999P002')) as mcreate:
            sample_name, sample_position = self.epp.next_sample_name_and_pos()
        assert sample_name == 'X99999P002A01'
        assert sample_position == 'A:1'
        for i in range(95):
            sample_name, sample_position = self.epp.next_sample_name_and_pos()
        assert sample_name == 'X99999P002H12'
        assert sample_position == 'H:12'
        assert mcreate.call_count == 1

    def test_create_samples(self):
        fem = FakeEntitiesMaker()
        self.epp.lims = fem.lims
        self.epp.process = fem.create_a_fake_process(**self.fem_params)
        self.epp.lims.get_containers = Mock(return_value=[])
        self.workflow_stage = Mock(uri='a_uri')
        self.patch_Step_create = patch('scripts.assign_workflow_preseqlab.Step.create', return_value=self.mocked_step)
        with self.get_patch_create_container(fem.create_a_fake_container(container_name='X99999P002')), \
             self.patched_get_workflow_stage as pws, self.patch_Step_create as psc:
            self.epp._run()


        expected_create_samples_list = [{
                'container': fem.object_store_per_type['Container'][1],
                'project': fem.object_store_per_type['Project'][0],
                'name': 'X99999P002A01', 'position': 'A:1',
                'udf': {'Prep Workflow': 'TruSeq Nano DNA Sample Prep',
                    'Coverage (X)': 30, 'Required Yield': 120,
                    'Species': 'Homo sapiens',
                    'Genome Version': 'hg38',
                    'Delivery': 'merged',
                    'Analysis Type': 'Variant Calling gatk',
                    'Rapid Analysis': 'No',
                    'User Prepared library': 'No'
                    }},
                {
                'container': fem.object_store_per_type['Container'][1],
                'project': fem.object_store_per_type['Project'][0],
                'name': 'X99999P002B01',
                'position': 'B:1',
                'udf': {'Prep Workflow': 'TruSeq PCR-Free DNA Sample Prep',
                    'Coverage (X)': 60, 'Required Yield': 240,
                    'Species': 'Mus musculus',
                    'Genome Version': 'hg19',
                    'Delivery': 'split',
                    'Analysis Type': 'None',
                    'Rapid Analysis': 'Yes',
                    'User Prepared library': 'Yes'}},

                ]

        self.epp.lims.create_batch.assert_called_once_with(Sample, expected_create_samples_list)
        pws.assert_any_call(self.epp.lims, 'PreSeqLab EG2.1 WF', 'Create Manifest EG 1.0 ST')
        pws.assert_any_call(self.epp.lims, "Remove From Processing EG 1.0 WF", "Remove From Processing EG 1.0 ST")

        #test step creation
        inputs_project_step_creation =[]
        inputs_project_step_creation_dict={self.epp.artifacts[0].samples[0].artifact.name:self.epp.artifacts[0].samples[0].artifact,
                                           self.epp.artifacts[1].samples[0].artifact.name:self.epp.artifacts[1].samples[0].artifact}
        for input in sorted(inputs_project_step_creation_dict):
            inputs_project_step_creation.append(inputs_project_step_creation_dict[input])

        psc.assert_called_with(
            self.epp.lims,
            inputs=inputs_project_step_creation,
            protocol_step=self.mocked_step,
            container_type_name='Tube'
        )

    def test_finish_step(self):
        # Successful attempt
        step = Mock()
        self.epp._finish_step(step)
        assert step.get.call_count == 1
        assert step.advance.call_count == 1

        # 3 failed attempts before raising
        step = Mock(
            advance=Mock(side_effect=HTTPError('400: Cannot advance a step that has an external program queued, '
                                               'running or pending acknowledgement'))
        )
        with patch('time.sleep'):
            with pytest.raises(HTTPError):
                self.epp._finish_step(step)
        assert step.get.call_count == 3
        assert step.advance.call_count == 3
