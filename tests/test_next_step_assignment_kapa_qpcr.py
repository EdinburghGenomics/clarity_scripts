from unittest.mock import Mock, patch, PropertyMock

from scripts.next_step_assignment_kapa_qpcr import AssignNextStepKAPAqPCR
from tests.test_common import TestEPP, NamedMock


#create a process with step UDF Standard Curve Result as pass and one as fail, and one with no value
#create input artifact with adjusted concentration greater than target and less than target

class TestAssignNextStepKAPAqPCR(TestEPP):
    def setUp(self):
        self.protostep = Mock(uri='http://test.com/config/protocols/1/step/2')
        self.actions = Mock(next_actions=[{'artifact':NamedMock(real_name='QSTD A')},
                                          {'artifact':NamedMock(real_name='No Template Control')},
                                          {'artifact': NamedMock(real_name='Library1', qc_flag='PASSED')},
                                          {'artifact': NamedMock(real_name='Library2', qc_flag='FAILED')}])


        self.patched_process1 = patch.object(
            AssignNextStepKAPAqPCR,
            'process',
            new_callable=PropertyMock(return_value=Mock(step=Mock(actions=self.actions, configuration=self.protostep),udf={'Standard Curve Result': 'Pass QSTD Curve'}))
        )

        self.patched_process2 = patch.object(
            AssignNextStepKAPAqPCR,
            'process',
            new_callable=PropertyMock(return_value=Mock(step=Mock(actions=self.actions, configuration=self.protostep
                                                                  ),udf={'Standard Curve Result':'Repeat Make and Read qPCR Quant'}))
        )

        self.patched_process3 = patch.object(
            AssignNextStepKAPAqPCR,
            'process',
            new_callable=PropertyMock(return_value=Mock(udf={'Standard Curver Result':''}))
        )

        self.epp = AssignNextStepKAPAqPCR(self.default_argv)


    def test_standard_curve_passed(self):
        protocol = Mock(steps=[self.protostep, Mock(), Mock()])
        patched_protocol = patch('scripts.next_step_assignment_kapa_qpcr.Protocol', return_value=protocol)

        with self.patched_process1, patched_protocol:
            self.epp._run()
            # artifacts with QSTD or No Template should be removed, libraries with QC flag as passed should be next step and
            # libraries with QC flag as failed should be review.
            expected_next_actions = [
                {'artifact':self.actions.next_actions[0]['artifact'],'action': 'remove'},
                {'artifact':self.actions.next_actions[1]['artifact'],'action': 'remove'},
                {'artifact':self.actions.next_actions[2]['artifact'],'action': 'nextstep', 'step': protocol.steps[1]},
                {'artifact':self.actions.next_actions[3]['artifact'],'action': 'review'}
            ]
            assert self.actions.next_actions == expected_next_actions
            assert self.actions.put.call_count == 1


    def test_standard_curve_failed(self):
        protocol = Mock(steps=[self.protostep, Mock(), Mock()])
        patched_protocol = patch('scripts.next_step_assignment_kapa_qpcr.Protocol', return_value=protocol)

        with self.patched_process2, patched_protocol:
            self.epp._run()
            # Ensure action is set to complete
            expected_next_actions = [
                {'artifact':self.actions.next_actions[0]['artifact'],'action': 'remove'},
                {'artifact':self.actions.next_actions[1]['artifact'],'action': 'remove'},
                {'artifact':self.actions.next_actions[2]['artifact'],'action': 'repeat'},
                {'artifact':self.actions.next_actions[3]['artifact'],'action': 'repeat'}
            ]
            assert self.actions.next_actions == expected_next_actions
            assert self.actions.put.call_count == 1


    def test_no_standard_curve_result(self):
        with self.patched_process3, patch('sys.exit') as mexit:
            self.epp._run()
            # Ensure that system exists

            mexit.assert_called_once_with(1)
