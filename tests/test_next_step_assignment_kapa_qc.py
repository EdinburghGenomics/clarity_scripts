from scripts.next_step_assignment_kapa_qc import AssignNextStep
from tests.test_common import TestEPP, NamedMock
from unittest.mock import Mock, patch, PropertyMock

def fake_outputs_per_input(inputid, ResultFile=True):
    # outputs_per_input is a list of all of the outputs per input obtained from the process by searching with input id
    # the outputs should have the container name and the location defined

    outputs = {
        'ai1': [Mock(id='ao1', udf={'KAPA Next Step':'KAPA Make Normalised Libraries'})],
        'ai2': [Mock(id='ao1', udf={'KAPA Next Step':'Sequencing Plate Preparation'})],
        'ai3': [Mock(id='ao1', udf={'KAPA Next Step': 'Request Repeats'})]


    }
    return outputs[inputid]

class TestAssignNextStep(TestEPP):
    def setUp(self):

        self.protostep =NamedMock(real_name='SeqPlatePrepST', uri='http://test.com/config/protocols/1/step/2')
        self.actions = Mock(next_actions=[{'artifact':Mock(id='ai1', samples=[Mock(id='ss1', artifact=Mock(id='sa1'))])},
                                          {'artifact':Mock(id='ai2', samples=[Mock(id='ss2', artifact=Mock(id='sa2'))])},
                                          {'artifact': Mock(id='ai3',samples=[Mock(id='ss3', artifact=Mock(id='sa3'))])}
                                           ])


        self.patched_process = patch.object(
            AssignNextStep,
            'process',
            new_callable=PropertyMock(return_value=Mock(outputs_per_input=fake_outputs_per_input,
                                                        step=Mock(actions=self.actions, configuration=self.protostep))
                                                        ))

        self.patched_get_workflow_stage = patch(
            'scripts.next_step_assignment_kapa_qc.get_workflow_stage',
            return_value=Mock(uri='a_uri')
        )

        self.epp = AssignNextStep(self.default_argv)

    def test_assign_next_step_seq_plate_prep(self): # show that samples are assigned to the next step and to Sequencing Plate Prep
        protocol = Mock(steps=[self.protostep, Mock(), Mock()])
        patched_protocol = patch('scripts.next_step_assignment_kapa_qc.Protocol', return_value=protocol)

        with self.patched_process, self.patched_lims, patched_protocol, self.patched_get_workflow_stage as pws:
            self.epp._run()
            # Ensure next step is set to the second step in the protocol
            expected_next_actions = [
                {'artifact':self.actions.next_actions[0]['artifact'],'action': 'nextstep', 'step': protocol.steps[1]},
                {'artifact':self.actions.next_actions[1]['artifact'],'action': 'remove'},
                {'artifact': self.actions.next_actions[2]['artifact'], 'action': 'remove'},
            ]
            assert expected_next_actions == self.actions.next_actions
            assert self.actions.put.call_count == 1


