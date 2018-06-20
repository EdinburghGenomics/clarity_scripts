from scripts.next_step_assignment_quantstudio_data_import import AssignNextStepQuantStudio
from tests.test_common import TestEPP
from unittest.mock import Mock, patch


fake_next_actions = [
    {'artifact': Mock(samples=[Mock(udf={'Number of Calls (Best Run)': 27})])},
    {'artifact': Mock(samples=[Mock(udf={'Number of Calls (Best Run)': 15})])}
]


class TestAssignNextStep(TestEPP):
    def setUp(self):
        self.patched_process = patch.object(
            AssignNextStepQuantStudio,
            'process',
            new=Mock(
                udf={'Minimum Number of Calls': 25},
                step=Mock(actions=Mock(next_actions=fake_next_actions))
            )
        )

        self.epp = AssignNextStepQuantStudio(
            'http://server:8080/a_step_uri',
            'a_user',
            'a_password',
            self.log_file
        )

    def test_assign_next_step_quant_studio(self):
        with self.patched_process:
            self.epp._run()

            assert fake_next_actions[0]['action'] == 'complete'
            assert fake_next_actions[0]['artifact'].samples[0].udf['QuantStudio QC'] == 'PASS'
            assert fake_next_actions[1]['action'] == 'review'
            assert fake_next_actions[1]['artifact'].samples[0].udf['QuantStudio QC'] == 'FAIL'
            assert self.epp.process.step.actions.put.call_count == 1
