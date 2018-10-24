from scripts.assign_workflow_preseqlab import AssignWorkflowPreSeqLab
from tests.test_common import TestEPP, fake_artifact
from unittest.mock import Mock, patch, PropertyMock


def fake_all_inputs(unique=False, resolve=False):
    """Return a list of mocked artifacts which contain samples which contain artifacts ... Simple!"""
    return (
        Mock(samples=[Mock(artifact=fake_artifact('a1'), id='s1', udf={'Proceed To SeqLab': True})]),
        Mock(samples=[Mock(artifact=fake_artifact('a2'), id='s2', udf={'Proceed To SeqLab': True, '2D Barcode': 'fluidX1'})]),
        Mock(samples=[Mock(artifact=fake_artifact('a3'), id='s3', udf={'Proceed To SeqLab': False})])
    )


class TestAssignWorkflowPreSeqLab(TestEPP):
    def setUp(self):
        self.patched_process = patch.object(
            AssignWorkflowPreSeqLab,
            'process',
            new_callable=PropertyMock(return_value=Mock(all_inputs=fake_all_inputs))
        )
        self.workflow_stage = Mock(uri='a_uri')
        self.patched_get_workflow_stage = patch(
            'scripts.assign_workflow_preseqlab.get_workflow_stage',
            return_value=self.workflow_stage
        )
        self.patch_find_art = patch(
            'scripts.assign_workflow_preseqlab.find_newest_artifact_originating_from',
            return_value=Mock(id='fx2')
        )
        self.mocked_step = Mock(details=Mock(udf={}), actions=Mock(next_actions=[{}]))
        self.patch_Step_create = patch('scripts.assign_workflow_preseqlab.Step.create', return_value=self.mocked_step)
        self.epp = AssignWorkflowPreSeqLab(self.default_argv)

    def test_assign(self):
        with self.patched_get_workflow_stage as pws, self.patched_lims, self.patched_process, self.patch_find_art, \
             self.patch_Step_create as psc:
            self.epp._run()

            pws.assert_called_any(self.epp.lims, 'PreSeqLab EG 6.0', 'Sequencing Plate Preparation EG 2.0')
            first_call = self.epp.lims.route_artifacts.call_args_list[0]
            assert sorted([a.id for a in first_call[0][0]]) == ['a1', 'fx2']
            assert first_call[1] == {'stage_uri': 'a_uri'}

            pws.assert_called_any(self.epp.lims, "Remove From Processing EG 1.0 WF", "Remove From Processing EG 1.0 ST")
            second_call = self.epp.lims.route_artifacts.call_args_list[1]
            assert sorted([a.id for a in second_call[0][0]]) == ['a3']
            assert second_call[1] == {'stage_uri': 'a_uri'}
            # Test the Step creation
            psc.assert_called_with(
                self.epp.lims,
                inputs=set([self.epp.artifacts[2].samples[0].artifact]),
                protocol_step=self.workflow_stage.step,
                container_type_name='Tube'
            )
            # Test udf in details
            assert 'Reason for removal from processing:' in self.mocked_step.details.udf
            self.mocked_step.details.put.assert_called_with()
            # Test next actions has been set.
            assert self.mocked_step.actions.next_actions == [{'action': 'complete'}]
            self.mocked_step.actions.put.assert_called_with()

            # Test advance has been called.
            assert self.mocked_step.advance.call_count == 2