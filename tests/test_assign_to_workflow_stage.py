from tests.test_common import fake_all_inputs, TestEPP
from unittest.mock import Mock, patch
from EPPs import assign_to_workflow_stage


class TestAsignWorkflowStage(TestEPP):
    def setUp(self):
        self.epp = assign_to_workflow_stage.AssignWorkflowStage(
            'http://server:8080/a_step_uri',
            'a_user',
            'a_password',
            self.log_file,
            'a_workflow_name',
            'a_stage_name',
            source='submitted'
        )
        self.epp._process = Mock(all_inputs=fake_all_inputs)
        self.epp._lims = Mock()

    def test_assign(self):
        with patch('EPPs.assign_to_workflow_stage.get_workflow_stage', return_value=Mock(uri='a_uri')) as p:
            self.epp._run()
            p.assert_called_with(self.epp.lims, self.epp.workflow_name, 'a_stage_name')
            exp_artifacts = ['artifact_for_sample_1', 'artifact_for_sample_2', 'artifact_for_sample_3']
            assert sorted(self.epp.lims.route_artifacts.call_args[0][0]) == exp_artifacts
            assert self.epp.lims.route_artifacts.call_args[1] == {'stage_uri': 'a_uri'}
