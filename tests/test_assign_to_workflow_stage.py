from unittest.mock import Mock, patch, PropertyMock
from EPPs.common import StepEPP
from scripts import assign_to_workflow_stage
from tests.test_common import fake_all_inputs, TestEPP


class TestAssignWorkflowStage(TestEPP):
    def setUp(self):
        argv = self.default_argv + [
            '--workflow', 'a_workflow_name',
            '--stage', 'a_stage_name',
            '--source', 'submitted'
        ]
        self.epp = assign_to_workflow_stage.AssignWorkflowStage(argv)
        self.epp2 = assign_to_workflow_stage.AssignWorkflowStage(argv + ['--only_once'])

    @patch.object(StepEPP, 'lims', new_callable=PropertyMock)
    @patch('scripts.assign_to_workflow_stage.get_workflow_stage', return_value=Mock(uri='a_uri'))
    def test_assign(self, mocked_workflow_stage, mocked_lims):
        with patch.object(StepEPP, 'process', new_callable=PropertyMock(return_value=Mock(all_inputs=fake_all_inputs))):
            self.epp._run()
            mocked_workflow_stage.assert_called_with(self.epp.lims, self.epp.workflow_name, 'a_stage_name')
            exp_artifacts = ['a1', 'a2']

            assert sorted([a.id for a in self.epp.lims.route_artifacts.call_args[0][0]]) == exp_artifacts
            assert self.epp.lims.route_artifacts.call_args[1] == {'stage_uri': 'a_uri'}

            mocked_workflow_stage.reset_mock()
            mocked_lims.reset_mock()

            self.epp2._run()
            mocked_workflow_stage.assert_called_with(self.epp2.lims, self.epp2.workflow_name, 'a_stage_name')
            assert self.epp2.lims.route_artifacts.call_count == 0
