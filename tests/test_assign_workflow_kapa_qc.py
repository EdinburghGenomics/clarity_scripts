from scripts.assign_workflow_kapa_qc import AssignWorkflow
from tests.test_common import TestEPP, NamedMock
from unittest.mock import Mock, patch, PropertyMock

class TestAssignNextStep(TestEPP):
    def setUp(self):

        self.protostep =NamedMock(real_name='SeqPlatePrepST', uri='http://test.com/config/protocols/1/step/2')
        self.actions = Mock(next_actions=[{'artifact':Mock(id='ai1', samples=[Mock(id='ss1', artifact=Mock(id='sa1'))],
                                                           udf={'KAPA Next Step':'KAPA Make Normalised Libraries'}),'action':'nextstep'},
                                          {'artifact':Mock(id='ai2',samples=[Mock(id='ss2', artifact=Mock(id='sa2'))],
                                                           udf={'KAPA Next Step':'Sequencing Plate Preparation'}),'action':'remove'},
                                           ])
        self.actions2 = Mock(next_actions=[{'artifact':Mock(id='ai1', samples=[Mock(id='ss1', artifact=Mock(id='sa1'))],
                                                           udf={'KAPA Next Step':'KAPA Make Normalised Libraries'}),'action':'nextstep'},
                                          {'artifact':Mock(id='ai2',samples=[Mock(id='ss2', artifact=Mock(id='sa2'))],
                                                           udf={'KAPA Next Step':'Request Repeats'}),'action':'remove'},
                                           ])
        self.actions3 = Mock(next_actions=[{'artifact':Mock(id='ai1', samples=[Mock(id='ss1', artifact=Mock(id='sa1'))],
                                                           udf={'KAPA Next Step':'KAPA Make Normalised Libraries'}),'action':'nextstep'},
                                          {'artifact':Mock(id='ai2',samples=[Mock(id='ss2', artifact=Mock(id='sa2'))],
                                                           udf={'KAPA Next Step':'Make and Read qPCR Quant'}),'action':'remove'},
                                           ])

        self.patched_process = patch.object(
            AssignWorkflow,
            'process',
            new_callable=PropertyMock(return_value=Mock(step=Mock(actions=self.actions, configuration=self.protostep))
                                                        ))

        self.patched_process2 = patch.object(
            AssignWorkflow,
            'process',
            new_callable=PropertyMock(return_value=Mock(step=Mock(actions=self.actions2, configuration=self.protostep))
                                                        ))
        self.patched_process3 = patch.object(
            AssignWorkflow,
            'process',
            new_callable=PropertyMock(return_value=Mock(step=Mock(actions=self.actions3, configuration=self.protostep))
                                                        ))

        self.patched_get_workflow_stage = patch(
            'scripts.assign_workflow_kapa_qc.get_workflow_stage',
            return_value=Mock(uri='a_uri')
        )

        self.epp = AssignWorkflow(self.default_argv + ['-sw', 'SeqPlatePrepWF'] + ['-ss', 'SeqPlatePrepST']
                                  + ['-rw', 'RepeatWF'] + ['-rs', 'RepeatST'] + ['-qw','MakeQPCRWF'] + ['-qs','MakeQPCRST'])

    def test_assign_next_step_seq_plate_prep(self): # show that samples are assigned to Sequencing Plate Prep
        protocol = Mock(steps=[self.protostep, Mock(), Mock()])
        patched_protocol = patch('scripts.next_step_assignment_kapa_qc.Protocol', return_value=protocol)

        with self.patched_process, self.patched_lims, patched_protocol, self.patched_get_workflow_stage as pws:
            self.epp._run()

            pws.assert_called_with(self.epp.lims, "SeqPlatePrepWF", "SeqPlatePrepST")

    def test_assign_next_step_request_repeats(self): # show that samples are assigned to request repeats
        protocol = Mock(steps=[self.protostep, Mock(), Mock()])
        patched_protocol = patch('scripts.next_step_assignment_kapa_qc.Protocol', return_value=protocol)

        with self.patched_process2, self.patched_lims, patched_protocol, self.patched_get_workflow_stage as pws:
            self.epp._run()

            pws.assert_called_with(self.epp.lims, "RepeatWF", "RepeatST")

    def test_assign_next_step_request_repeats(self): # show that samples are assigned to request repeats
        protocol = Mock(steps=[self.protostep, Mock(), Mock()])
        patched_protocol = patch('scripts.next_step_assignment_kapa_qc.Protocol', return_value=protocol)

        with self.patched_process3, self.patched_lims, patched_protocol, self.patched_get_workflow_stage as pws:
            self.epp._run()

            pws.assert_called_with(self.epp.lims, "MakeQPCRWF", "MakeQPCRST")