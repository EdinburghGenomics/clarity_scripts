from scripts.next_step_assignment import AssignNextStep
from tests.test_common import TestEPP
from unittest.mock import Mock, patch, PropertyMock


class TestAssignNextStep(TestEPP):
    def setUp(self):
        self.protostep = Mock(uri='http://test.com/config/protocols/1/step/2')
        self.actions = Mock(next_actions=[{}, {}])

        self.patched_process = patch.object(
            AssignNextStep,
            'process',
            new_callable=PropertyMock(return_value=Mock(step=Mock(actions=self.actions, configuration=self.protostep)))
        )

        self.epp = AssignNextStep(self.default_argv)
        self.epp_review = AssignNextStep(self.default_argv + ['-r'])
        self.epp_remove = AssignNextStep(self.default_argv + ['-e'])

    def test_assign_next_step(self):
        protocol = Mock(steps=[self.protostep, Mock(), Mock()])
        patched_protocol = patch('EPPs.common.Protocol', return_value=protocol)

        with self.patched_process, patched_protocol:
            self.epp._run()
            # Ensure next step is set to the second step in the protocol
            expected_next_actions = [
                {'action': 'nextstep', 'step': protocol.steps[1]},
                {'action': 'nextstep', 'step': protocol.steps[1]}
            ]
            assert self.actions.next_actions == expected_next_actions
            assert self.actions.put.call_count == 1

        protocol = Mock(steps=[Mock(), self.protostep, Mock()])
        patched_protocol = patch('EPPs.common.Protocol', return_value=protocol)

        self.actions.put.reset_mock()
        with self.patched_process, patched_protocol:
            self.epp._run()
            # Ensure next step is set to the third step in the protocol
            expected_next_actions = [
                {'action': 'nextstep', 'step': protocol.steps[2]},
                {'action': 'nextstep', 'step': protocol.steps[2]}
            ]
            assert self.actions.next_actions == expected_next_actions
            assert self.actions.put.call_count == 1

    def test_assign_complete(self):
        protocol = Mock(steps=[Mock(), Mock(), self.protostep])
        patched_protocol = patch('EPPs.common.Protocol', return_value=protocol)

        with self.patched_process, patched_protocol:
            self.epp._run()
            # Ensure action is set to complete
            expected_next_actions = [
                {'action': 'complete'},
                {'action': 'complete'}
            ]
            assert self.actions.next_actions == expected_next_actions
            assert self.actions.put.call_count == 1

    def test_assign_review(self):
        with self.patched_process:
            self.epp_review._run()
            # Ensure action is set to review
            expected_next_actions = [
                {'action': 'review'},
                {'action': 'review'}
            ]
            assert self.actions.next_actions == expected_next_actions
            assert self.actions.put.call_count == 1

    def test_assign_remove(self):
        with self.patched_process:
            self.epp_remove._run()
            # Ensure action is set to remove
            expected_next_actions = [
                {'action': 'remove'},
                {'action': 'remove'}
            ]
            assert self.actions.next_actions == expected_next_actions
            assert self.actions.put.call_count == 1
