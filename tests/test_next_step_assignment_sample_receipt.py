from unittest.mock import patch, PropertyMock, Mock

from scripts.next_step_assignment_sample_receipt import AssignNextStepSampleReceipt
from tests.test_common import TestEPP, NamedMock


class TestNextStepSampleReceipt(TestEPP):
    protostep1 = NamedMock(real_name='next_step1', uri='http://test.com/config/protocols/1/step/2')
    protostep2 = NamedMock(real_name='next_step2', uri='http://test.com/config/protocols/1/step/3')
    protostep3 = NamedMock(real_name='next_step3', uri='http://test.com/config/protocols/1/step/3')

    protocol = Mock(steps=[protostep1, protostep2, protostep3])

    patched_protocol= patch('EPPs.common.Protocol', return_value=protocol)

    udfs1 = {
        'Dry ice remaining in package?': 'Yes',
        'Container(s) undamaged and sealed?': 'Yes',
        'Samples frozen?': 'Yes',
        '>= 50ul sample present in wells or tubes?': 'Yes'
    }

    udfs2 = {
        'Dry ice remaining in package?': 'No',
        'Container(s) undamaged and sealed?': 'Yes',
        'Samples frozen?': 'Yes',
        '>= 50ul sample present in wells or tubes?': 'Yes'
    }

    udfs3 = {
        'Dry ice remaining in package?': 'Yes',
        'Container(s) undamaged and sealed?': 'No',
        'Samples frozen?': 'Yes',
        '>= 50ul sample present in wells or tubes?': 'Yes'
    }

    udfs4 = {
        'Dry ice remaining in package?': 'Yes',
        'Container(s) undamaged and sealed?': 'Yes',
        'Samples frozen?': 'No',
        '>= 50ul sample present in wells or tubes?': 'Yes'
    }

    udfs5 = {
        'Dry ice remaining in package?': 'Yes',
        'Container(s) undamaged and sealed?': 'Yes',
        'Samples frozen?': 'Yes',
        '>= 50ul sample present in wells or tubes?': 'No'
    }

    protostep = Mock(uri='http://test.com/config/protocols/1/step/2')

    def setUp(self):
        self.epp = AssignNextStepSampleReceipt(self.default_argv)
        self.actions = Mock(next_actions=[{}])

        self.step1 = Mock(configuration=self.protostep1,
                          actions=self.actions)
        self.step2 = Mock(configuration=self.protostep3,
                          actions=self.actions)

        self.patched_process1 = patch.object(
            AssignNextStepSampleReceipt,
            'process',
            new_callable=PropertyMock(return_value=Mock(
                step=self.step1,
                udf=self.udfs1

            ))
        )

        self.patched_process2 = patch.object(
            AssignNextStepSampleReceipt,
            'process',
            new_callable=PropertyMock(return_value=Mock(
                step=self.step2,
                udf=self.udfs1

            ))
        )

        self.patched_process3 = patch.object(
            AssignNextStepSampleReceipt,
            'process',
            new_callable=PropertyMock(return_value=Mock(
                step=self.step1,
                udf=self.udfs2

            ))
        )

        self.patched_process4 = patch.object(
            AssignNextStepSampleReceipt,
            'process',
            new_callable=PropertyMock(return_value=Mock(
                step=self.step1,
                udf=self.udfs3

            ))
        )

        self.patched_process5 = patch.object(
            AssignNextStepSampleReceipt,
            'process',
            new_callable=PropertyMock(return_value=Mock(
                step=self.step1,
                udf=self.udfs4

            ))
        )

        self.patched_process6 = patch.object(
            AssignNextStepSampleReceipt,
            'process',
            new_callable=PropertyMock(return_value=Mock(
                step=self.step1,
                udf=self.udfs5

            ))
        )

    def test_next_step_happy_path(self):  # current step not last step in protocol
        with self.patched_process1, self.patched_protocol:
            self.epp._run()

            expected_next_actions = [{
                'action': 'nextstep',
                'step': self.protostep2}]

            assert self.epp.process.step.actions.next_actions == expected_next_actions
            assert self.epp.process.step.actions.put.call_count == 1

    def test_next_step_happy_path2(self):  # current step is last in protocol
        with self.patched_process2, self.patched_protocol:
            self.epp._run()

            expected_next_actions = [{
                'action': 'complete'}]

            assert self.epp.process.step.actions.next_actions == expected_next_actions
            assert self.epp.process.step.actions.put.call_count == 1

    def test_next_step_no_dry_ice(self):
        with self.patched_process3, self.patched_protocol:
            self.epp._run()

            expected_next_actions = [{
                'action': 'review'}]

            assert self.epp.process.step.actions.next_actions == expected_next_actions
            assert self.epp.process.step.actions.put.call_count == 1

    def test_next_step_damaged(self):
        with self.patched_process4, self.patched_protocol:
            self.epp._run()

            expected_next_actions = [{
                'action': 'review'}]

            assert self.epp.process.step.actions.next_actions == expected_next_actions
            assert self.epp.process.step.actions.put.call_count == 1

    def test_next_step_unfrozen(self):
        with self.patched_process5, self.patched_protocol:
            self.epp._run()

            expected_next_actions = [{
                'action': 'review'}]

            assert self.epp.process.step.actions.next_actions == expected_next_actions
            assert self.epp.process.step.actions.put.call_count == 1

    def test_next_step_samples_not_present(self):
        with self.patched_process5, self.patched_protocol:
            self.epp._run()

            expected_next_actions = [{
                'action': 'review'}]

            assert self.epp.process.step.actions.next_actions == expected_next_actions
            assert self.epp.process.step.actions.put.call_count == 1
