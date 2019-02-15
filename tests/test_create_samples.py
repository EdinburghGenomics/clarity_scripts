from unittest.mock import patch, Mock, PropertyMock

from tests.test_common import TestEPP, NamedMock

from scripts.create_samples import CreateSamples, Container

class TestCreateSamples(TestEPP):
    container1 = NamedMock(real_name='container1', type=NamedMock(real_name='96 well plate'))
    container2 = NamedMock(real_name='container1', type=NamedMock(real_name='rack 96 positions'))
    container3 = NamedMock(real_name='container1', type=NamedMock(real_name='SGP rack 96 positions'))

    sample1 = Mock(project=NamedMock(real_name='project1'), container=container1)
    artifact1 = Mock(samples=[sample1])

    patched_process1 = patch.object(
        CreateSamples,
        'process',
        new_callable=PropertyMock(return_value=Mock(
            all_inputs=Mock(return_value=[artifact1])
        ))
    )

    patched_get_workflow_stage = patch(
        'scripts.create_samples.get_workflow_stage',
        return_value=Mock(uri='a_uri')
    )

    def setUp(self):

        self.epp=CreateSamples(self.default_argv)

    def test_create_sample_96_well_plate(self):
        with self.patched_process1, self.patched_lims, self.patched_get_workflow_stage:
            self.epp._run()
