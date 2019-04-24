from unittest.mock import patch, PropertyMock, Mock

from scripts.next_step_assignment_spectramax import AssignmentNextStepSpectramax
from tests.test_common import TestEPP, NamedMock


def fake_outputs_per_input(id,ResultFile=None):
    fake_outputs = {
        'ai1': [Mock(udf={})],
        'ai2': [Mock(udf={})],
        'ai3': [Mock(udf={'Repeat Picogreen with 1:10 Dilution?': True})],
        'ai4': [Mock(udf={})],
    }
    return fake_outputs[id]


class TestAssignmentNextStepSpectramax(TestEPP):

    def setUp(self):
        self.protostep = NamedMock(real_name='SeqPlatePrepST', uri='http://test.com/config/protocols/1/step/2')
        self.actions = Mock(
            next_actions=[{'artifact': Mock(id='ai1', samples=[Mock(udf={})])},
                          {'artifact': Mock(id='ai2', samples=[Mock(udf={'Prep Workflow': 'KAPA DNA Sample Prep'})])},
                          {'artifact': Mock(id='ai3', samples=[Mock(udf={})])},
                          {'artifact': Mock(id='ai4',
                                            samples=[Mock(udf={'PreSeqLab Fragment Analyser Complete': True})])}
                          ]
        )

        self.patched_process = patch.object(
            AssignmentNextStepSpectramax,
            'process',
            new_callable=PropertyMock(return_value=Mock(
                step=Mock(actions=self.actions, configuration=self.protostep), outputs_per_input=fake_outputs_per_input)
            ))

        self.protocol = Mock(steps=[self.protostep, Mock(), Mock(), Mock()])
        self.patched_protocol = patch('scripts.next_step_assignment_spectramax.Protocol', return_value=self.protocol)
        self.epp = AssignmentNextStepSpectramax(self.default_argv)

    def test_next_step_assignment_spectramax(self):
        with self.patched_protocol, self.patched_process:
            self.epp._run()

            expected_next_actions = [
                {'artifact': self.epp.process.step.actions.next_actions[0]['artifact'], 'action': 'nextstep',
                 'step': self.protocol.steps[1]},
                {'artifact': self.epp.process.step.actions.next_actions[1]['artifact'], 'action': 'nextstep',
                 'step': self.protocol.steps[2]},
                {'artifact': self.epp.process.step.actions.next_actions[2]['artifact'], 'action': 'nextstep',
                 'step': self.protocol.steps[3]},
                {'artifact': self.epp.process.step.actions.next_actions[3]['artifact'], 'action': 'nextstep',
                 'step': self.protocol.steps[2]}
            ]

            actual_next_actions = self.epp.process.step.actions.next_actions

            assert expected_next_actions == actual_next_actions
