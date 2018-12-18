from unittest.mock import Mock, patch, PropertyMock

from scripts.next_step_assignment_kapa_qc import AssignNextStep
from tests.test_common import TestEPP, NamedMock


class TestAssignNextStep(TestEPP):
    def setUp(self):
        self.protostep = NamedMock(real_name='SeqPlatePrepST', uri='http://test.com/config/protocols/1/step/2')
        self.actions = Mock(
            next_actions=[{'artifact': Mock(id='ai1', udf={'KAPA Next Step': 'KAPA Make Normalised Libraries'})},
                          {'artifact': Mock(id='ai2', udf={'KAPA Next Step': 'Sequencing Plate Preparation'})},
                          {'artifact': Mock(id='ai3', udf={'KAPA Next Step': 'Request Repeats'})}
                          ])

        self.patched_process = patch.object(
            AssignNextStep,
            'process',
            new_callable=PropertyMock(return_value=Mock(
                step=Mock(actions=self.actions, configuration=self.protostep))
            ))

        self.epp = AssignNextStep(self.default_argv)

    def test_assign_next_step_seq_plate_prep(
            self):  # show that samples are assigned to the next step and to Sequencing Plate Prep
        protocol = Mock(steps=[self.protostep, Mock(), Mock()])
        patched_protocol = patch('scripts.next_step_assignment_kapa_qc.Protocol', return_value=protocol)

        with self.patched_process, self.patched_lims, patched_protocol:
            self.epp._run()
            # Ensure next step is set to the second step in the protocol
            expected_next_actions = [
                {'artifact': self.actions.next_actions[0]['artifact'], 'action': 'nextstep', 'step': protocol.steps[1]},
                {'artifact': self.actions.next_actions[1]['artifact'], 'action': 'remove'},
                {'artifact': self.actions.next_actions[2]['artifact'], 'action': 'remove'},
            ]

            assert expected_next_actions == self.actions.next_actions
            assert self.actions.put.call_count == 1
