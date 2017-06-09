from EPPs.common import StepEPP
from scripts.assign_workflow_preseqlab import AssignWorkflowPreSeqLab
from tests.test_common import TestEPP, fake_artifact
from unittest.mock import Mock, patch, PropertyMock, MagicMock


def fake_all_inputs(unique=False, resolve=False):
    '''Return a list of mocked artifacts which contain sample which contain artifact ... Simple!'''
    return (
        Mock(samples=[Mock(artifact=fake_artifact(id='a1'), id='s1', udf={"Proceed To SeqLab": True})]),
        Mock(samples=[Mock(artifact=fake_artifact(id='a2'), id='s2', udf={"Proceed To SeqLab": True})])
    )

def fake_all_inputs_fluidx(unique=False, resolve=False):
    '''Return a list of mocked artifacts which contain sample which contain artifact marked as fluidX... Simple!'''
    return (
        Mock(samples=[Mock(artifact=fake_artifact(id='a1'), id='s1', udf={
            "Proceed To SeqLab": True,
            "2D Barcode": 'fluidX1'
        })]),
    )


class MockedLims(MagicMock):
    def get_artifacts(*args, **kwargs):
        return [
            Mock(id='fx1', parent_process=Mock(id='121')),
            Mock(id='fx2', parent_process=Mock(id='123'))
        ]



class TestAssignWorkflowPreSeqLab(TestEPP):
    def setUp(self):
        self.patched_process = patch.object(
            AssignWorkflowPreSeqLab,
            'process',
            new_callable=PropertyMock(return_value=Mock(all_inputs=fake_all_inputs))
        )
        self.patched_process_fluidx = patch.object(
            AssignWorkflowPreSeqLab,
            'process',
            new_callable=PropertyMock(return_value=Mock(all_inputs=fake_all_inputs_fluidx))
        )

        self.patched_lims = patch.object(AssignWorkflowPreSeqLab, 'lims', new_callable=PropertyMock)
        self.patched_get_workflow_stage = patch(
            'scripts.assign_workflow_preseqlab.get_workflow_stage',
            return_value=Mock(uri='a_uri')
        )

        self.epp = AssignWorkflowPreSeqLab(
            'http://server:8080/a_step_uri',
            'a_user',
            'a_password',
            self.log_file
        )

    def test_assign(self):
        with self.patched_get_workflow_stage as pws, self.patched_lims, self.patched_process:
            self.epp._run()

            pws.assert_called_with(self.epp.lims, 'PreSeqLab EG 6.0', 'Sequencing Plate Preparation EG 2.0')
            assert sorted([a.id for a in self.epp.lims.route_artifacts.call_args[0][0]]) == ['a1', 'a2']
            assert self.epp.lims.route_artifacts.call_args[1] == {'stage_uri': 'a_uri'}

    def test_assign_fluidx(self):
        with self.patched_get_workflow_stage as pws, self.patched_lims as pl, self.patched_process_fluidx:
            pl.return_value = MockedLims()
            self.epp._run()

            pws.assert_called_with(self.epp.lims, 'PreSeqLab EG 6.0', 'Sequencing Plate Preparation EG 2.0')
            assert sorted([a.id for a in self.epp.lims.route_artifacts.call_args[0][0]]) == ['fx2']
            assert self.epp.lims.route_artifacts.call_args[1] == {'stage_uri': 'a_uri'}