from unittest.mock import Mock, patch, PropertyMock

from scripts.next_step_assignment_imp_ssqc import AssignNextStep
from tests.test_common import TestEPP, NamedMock


class TestAssignNextStep(TestEPP):
    def setUp(self):
        self.protostep1 = NamedMock(real_name='Make KAPA Libraries EG 1.1 ST', uri='http://test.com/config/protocols/1/step/2')
        self.protostep2 = NamedMock(real_name='KAPA GX QC EG 1.0 ST', uri='http://test.com/config/protocols/1/step/2')

        self.actions = Mock(next_actions=[
            {'artifact': NamedMock(real_name='SDNA A1', location=[NamedMock(real_name='LP9999999-IMP'),'well'])},
            {'artifact': NamedMock(real_name='SDNA A1', location=[NamedMock(real_name='LP9999999-SSQC'), 'well'])},
            ])

        self.patched_process1 = patch.object(
            AssignNextStep,
            'process',
            new_callable=PropertyMock(return_value=Mock(step=Mock(actions=self.actions, configuration=Mock(uri='uri'))))
        )

        self.epp = AssignNextStep(self.default_argv + ['-m','Make KAPA Libraries EG 1.1 ST'] + ['-q','KAPA GX QC EG 1.0 ST'])

    def test_happy_path(self):
        protocol =Mock(steps=[self.protostep1, self.protostep2, Mock()])
        patched_protocol = patch('scripts.next_step_assignment_imp_ssqc.Protocol', return_value=protocol)
        with self.patched_process1, patched_protocol:
            self.epp._run()
            # samples in IMP should be assigned to Make KAPA LIbraries EG 1.1 ST and samples on SSQC should be assigned to KAPA GX QC EG 1.0 ST

            assert self.actions.next_actions[0]['action'] == 'nextstep'
            assert self.actions.next_actions[0]['step'].name == 'Make KAPA Libraries EG 1.1 ST'
            assert self.actions.next_actions[1]['action'] == 'nextstep'
            assert self.actions.next_actions[1]['step'].name == 'KAPA GX QC EG 1.0 ST'
            assert self.actions.put.call_count == 1
