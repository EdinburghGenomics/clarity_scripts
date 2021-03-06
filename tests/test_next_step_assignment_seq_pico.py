from unittest.mock import Mock, patch, PropertyMock

from scripts.next_step_assignment_seq_pico import AssignNextStepSeqPico
from tests.test_common import TestEPP, NamedMock


# create a process with step UDF Standard Curve Result as pass and one as fail, and one with no value
# create input artifact with adjusted concentration greater than target and less than target

class TestAssignNextStepKAPAqPCR(TestEPP):
    def setUp(self):
        self.actions = Mock(next_actions=[
            {'artifact': NamedMock(real_name='SDNA A1', udf={'Picogreen Conc Review': 'FAIL,<Minimum DNA Conc.'})},
            {'artifact': NamedMock(real_name='Library1', udf={'Picogreen Conc Review': 'PASS'})},
            {'artifact': NamedMock(real_name='Library2', udf={'Picogreen Conc Review': 'FAIL,<Minimum DNA Conc.'})}])

        self.patched_process1 = patch.object(
            AssignNextStepSeqPico,
            'process',
            new_callable=PropertyMock(return_value=Mock(step=Mock(actions=self.actions)))
        )

        self.epp = AssignNextStepSeqPico(self.default_argv)

    def test_happy_path(self):

        with self.patched_process1:
            self.epp._run()
            # artifacts with SDNA in the name should be removed,
            # libraries with QC flag as passed should be next step and
            # libraries with QC flag as failed should be review.
            expected_next_actions = [
                {'artifact': self.actions.next_actions[0]['artifact'], 'action': 'remove'},
                {'artifact': self.actions.next_actions[1]['artifact'], 'action': 'complete'},
                {'artifact': self.actions.next_actions[2]['artifact'], 'action': 'review'}
            ]
            assert self.actions.next_actions == expected_next_actions
            assert self.actions.put.call_count == 1
