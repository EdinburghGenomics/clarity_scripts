from unittest.mock import Mock, patch, PropertyMock, call

from scripts.assign_workflow_receive_sample import AssignWorkflowReceiveSample
from tests.test_common import TestEPP


def fake_all_inputs(unique=False, resolve=False):
    """Return a list of mocked artifacts which contain samples with UDFs"""
    return (
        Mock(id='ai1', samples=[Mock(udf={'User Prepared Library': 'Yes'})]),
        Mock(id='ai2', samples=[Mock(udf={'User Prepared Library': 'No'})])
    )


class TestAssignWorkflowReceiveSample(TestEPP):
    def setUp(self):
        self.patched_process = patch.object(
            AssignWorkflowReceiveSample,
            'process',
            new_callable=PropertyMock(return_value=Mock(all_inputs=fake_all_inputs))
        )
        self.patched_lims = patch.object(AssignWorkflowReceiveSample, 'lims', new_callable=PropertyMock)
        self.patched_get_workflow_stage = patch(
            'scripts.assign_workflow_receive_sample.get_workflow_stage',
            return_value=Mock(uri='a_uri')
        )
        self.epp = AssignWorkflowReceiveSample(
            'http://server:8080/a_step_uri',
            'a_user',
            'a_password',
            self.log_file
        )

    def test_assign(self):
        with self.patched_get_workflow_stage as pws, self.patched_lims, self.patched_process:
            self.epp._run()

            pws.assert_has_calls((
                call(self.epp.lims, "User Prepared Library Receipt and Batch EG 1.0 WF",
                     "User Prepared Library Plate Receipt EG 1.0 ST"),
                call(self.epp.lims, "PreSeqLab EG 6.0", "Receive Sample 6.1")
            ))
            # first routing (user prepared library)
            route_args = self.epp.lims.route_artifacts.call_args_list[0]
            assert sorted([a.id for a in route_args[0][0]]) == ['ai1']
            assert self.epp.lims.route_artifacts.call_args[1] == {'stage_uri': 'a_uri'}

            # second routing (not user prepared library)
            route_args = self.epp.lims.route_artifacts.call_args_list[1]
            assert sorted([a.id for a in route_args[0][0]]) == ['ai2']
