from scripts.next_step_assignment_quantstudio_data_import import AssignNextStepQuantStudio
from tests.test_common import TestEPP, fake_artifact
from unittest.mock import Mock, patch, PropertyMock


def fake_next_actions(unique=False, resolve=False):
    """Return a list of mocked artifacts which contain samples which contain artifacts ... Simple!"""
    return [
        {'artifact': Mock(samples=[Mock(udf={'Number of Calls (Best Run)': 27})])},
        {'artifact': Mock(samples=[Mock(udf={'Number of Calls (Best Run)': 15})])}
    ]


class TestAssignNextStep(TestEPP):
    def setUp(self):
        self.patched_process = patch.object(
            AssignNextStepQuantStudio,
            'process',
            new_callable=PropertyMock(
                return_value=Mock(
                    udf={
                        'Minimum Number of Calls': 25,
                    },
                    step=Mock(
                        actions=Mock(
                            next_actions=fake_next_actions()
                        )
                    )
                )
            )
        )

        self.epp = AssignNextStepQuantStudio(self.default_argv)

    def test_assign_next_step_quant_studio(self):
        with self.patched_process:
            self.epp._run()

            assert self.epp.process.step.actions.next_actions[0]['action'] == 'complete'
            assert self.epp.process.step.actions.next_actions[0]['artifact'].samples[0].udf.get(
                'QuantStudio QC') == "PASS"
            assert self.epp.process.step.actions.next_actions[1]['action'] == 'review'
            assert self.epp.process.step.actions.next_actions[1]['artifact'].samples[0].udf.get(
                'QuantStudio QC') == "FAIL"
            assert self.epp.process.step.actions.put.call_count == 1
