from unittest.mock import Mock, patch, PropertyMock

from scripts.next_step_assignment_gx import AssignNextStep
from tests.test_common import TestEPP, NamedMock


class TestAssignNextStep(TestEPP):
    def setUp(self):

        self.actions = Mock(next_actions=[
            {'artifact': NamedMock(real_name='Sample1',udf={'SSQC Result':'PASSED'} )},
            {'artifact': NamedMock(real_name='Sample2', udf={'SSQC Result':'FAILED'})},
            ])

        self.patched_process1 = patch.object(
            AssignNextStep,
            'process',
            new_callable=PropertyMock(return_value=Mock(step=Mock(actions=self.actions, configuration=Mock(uri='uri'))))
        )

        self.epp = AssignNextStep(self.default_argv)

    def test_happy_path(self):
        with self.patched_process1:
            self.epp._run()
            # samples in IMP should be assigned to Make KAPA LIbraries EG 1.1 ST and samples on SSQC should be assigned to KAPA GX QC EG 1.0 ST

            assert self.actions.next_actions[0]['action'] == 'remove'
            assert self.actions.next_actions[1]['action'] == 'review'
            assert self.actions.put.call_count == 1
