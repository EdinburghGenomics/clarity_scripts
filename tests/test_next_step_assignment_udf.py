from unittest.mock import patch, PropertyMock, Mock

import pytest

from EPPs.common import StepEPP
from tests.test_common import TestEPP, NamedMock

from scripts.next_step_assignment_udf import AssignNextStepUDF

class TestNextStepAssignmentUDF(TestEPP):

    step_udfs1={'step_udf1':'udf_value1'}
    step_udfs2={'step_udf1':'udf_value2'}
    step_udfs3={'step_udf2':'udf_value3'}

    protostep1 = NamedMock(real_name='next_step1',uri='http://test.com/config/protocols/1/step/2')
    protostep2 = NamedMock(real_name='next_step2', uri='http://test.com/config/protocols/1/step/3')
    protostep3 = NamedMock(real_name='next_step3', uri='http://test.com/config/protocols/1/step/3')

    actions = Mock(next_actions=[{}])

    protocol = Mock(steps=[protostep1, protostep2, protostep3])

    patched_protocol = patch('scripts.next_step_assignment_udf.Protocol', return_value=protocol)

    patched_process1= patch.object(
        StepEPP,
        'process',
        new_callable=PropertyMock(return_value=Mock(
            udf=step_udfs1,
            step=Mock(
                actions=actions,
                configuration=protostep1)
        )
                                  )
    )

    patched_process2= patch.object(
        StepEPP,
        'process',
        new_callable=PropertyMock(return_value=Mock(
            udf=step_udfs2,
            step=Mock(
                actions=actions,
                configuration=protostep1)
        )
                                  )
    )

    patched_process3= patch.object(
        StepEPP,
        'process',
        new_callable=PropertyMock(return_value=Mock(
            udf=step_udfs3,
            step=Mock(
                actions=actions,
                configuration=protostep1)
        )
                                  )
    )



    def setUp(self):
        self.epp = AssignNextStepUDF(self.default_argv
                                     +['--step_udf','step_udf1']
                                     +['--udf_values','udf_value1']
                                     +['--next_steps','next_step3'])


    def test_next_step_udf_happy_path(self): #next step is the step defined by the next_steps argument
        with self.patched_process1, self.patched_protocol:
            self.epp._run()

            expected_next_actions = [
                {'action': 'nextstep','step': self.protocol.steps[2]}

            ]

            assert self.actions.next_actions == expected_next_actions
            assert self.actions.put.call_count == 1
            self.actions.put.reset_mock()

    def test_next_step_udf_udf_value_false(self): #next action is the next step in protocol
        with self.patched_process2, self.patched_protocol:
            self.epp._run()

            expected_next_actions = [
                {'action': 'nextstep','step': self.protocol.steps[1]}

            ]

            assert self.actions.next_actions == expected_next_actions
            assert self.actions.put.call_count == 1

    def test_next_step_udf_step_udf_not_present(self): #error message as step_udf defined by argument not present
        with self.patched_process3, self.patched_protocol, pytest.raises(ValueError) as e:
            self.epp._run()
        assert str(e.value) == 'Step UDF step_udf1 not present'