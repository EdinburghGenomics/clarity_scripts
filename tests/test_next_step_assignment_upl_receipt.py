from scripts.next_step_assignment_user_prepared_plate_receipt import AssignNextStepUPL
from tests.test_common import TestEPP
from unittest.mock import Mock, patch, PropertyMock


class TestAssignNextStepUPL(TestEPP):
    def setUp(self):

        self.protostep = Mock(uri='http://test.com/config/protocols/1/step/2')
        self.actions = Mock(next_actions=[{}, {}])

        step_udfs1 = {
            'Plate(s) Undamaged and Sealed?': 'Yes',
            'Samples Present and Frozen in Wells?': 'Yes',
        }

        step_udfs2 = {
            'Plate(s) Undamaged and Sealed?': 'No',
            'Samples Present and Frozen in Wells?': 'Yes',
        }

        step_udfs3 = {
            'Plate(s) Undamaged and Sealed?': 'No',
            'Samples Present and Frozen in Wells?': 'No',
        }
        step_udfs4 = {
            'Plate(s) Undamaged and Sealed?': 'Yes',
            'Samples Present and Frozen in Wells?': 'No',
        }

        self.patched_process1 = patch.object(
            AssignNextStepUPL,
            'process',
            new_callable=PropertyMock(return_value=Mock(step=Mock(actions=self.actions, configuration=self.protostep), udf=step_udfs1))
        )

        self.patched_process2 = patch.object(
            AssignNextStepUPL,
            'process',
            new_callable=PropertyMock(return_value=Mock(step=Mock(actions=self.actions, configuration=self.protostep), udf=step_udfs2))
        )
        self.patched_process3 = patch.object(
            AssignNextStepUPL,
            'process',
            new_callable=PropertyMock(return_value=Mock(step=Mock(actions=self.actions, configuration=self.protostep), udf=step_udfs3))
        )
        self.patched_process4 = patch.object(
            AssignNextStepUPL,
            'process',
            new_callable=PropertyMock(return_value=Mock(step=Mock(actions=self.actions, configuration=self.protostep), udf=step_udfs4))
        )


        self.epp = AssignNextStepUPL(
            'http://server:8080/a_step_uri',
            'a_user',
            'a_password',
            self.log_file
        )

    def test_assign_next_step_udfs1(self):
        protocol = Mock(steps=[self.protostep, Mock(), Mock()])
        patched_protocol = patch('scripts.next_step_assignment_user_prepared_plate_receipt.Protocol', return_value=protocol)

        with self.patched_process1, patched_protocol:
            self.epp._run()
            # Ensure next step is set to the second step in the protocol
            expected_next_actions = [
                {'action': 'nextstep', 'step': protocol.steps[1]},
                {'action': 'nextstep', 'step': protocol.steps[1]}
            ]
            assert self.actions.next_actions == expected_next_actions
            assert self.actions.put.call_count == 1

        self.actions.put.reset_mock()

    def test_assign_next_step_udfs2(self):
        with self.patched_process2:
            self.epp._run()
            # Ensure next step is set to the second step in the protocol
            expected_next_actions = [
                {'action': 'review'},
                {'action': 'review'}
            ]

            assert self.actions.next_actions == expected_next_actions
            assert self.actions.put.call_count == 1

        self.actions.put.reset_mock()

    def test_assign_next_step_udfs3(self):
        with self.patched_process3:
            self.epp._run()
            # Ensure next step is set to the second step in the protocol
            expected_next_actions = [
                {'action': 'review'},
                {'action': 'review'}
            ]
            assert self.actions.next_actions == expected_next_actions
            assert self.actions.put.call_count == 1

        self.actions.put.reset_mock()

    def test_assign_next_step_udfs4(self):
        with self.patched_process4:
            self.epp._run()
            # Ensure next step is set to the second step in the protocol
            expected_next_actions = [
                {'action': 'review'},
                {'action': 'review'}
            ]
            assert self.actions.next_actions == expected_next_actions
            assert self.actions.put.call_count == 1

        self.actions.put.reset_mock()



