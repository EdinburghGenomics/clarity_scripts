from unittest.mock import Mock, patch, PropertyMock, call

from scripts.assign_workflow_post_receive_sample import AssignWorkflowPostReceiveSample
from tests.test_common import TestEPP, NamedMock


def fake_all_inputs(unique=False, resolve=False):
    """Return a list of mocked artifacts which contain samples with UDFs and a container"""

    return (
        Mock(id='ai1', samples=[
            Mock(udf={'User Prepared Library': 'No'}, container=Mock(type=NamedMock(real_name='rack 96 positions')))]),
        Mock(id='ai2', samples=[
            Mock(udf={'User Prepared Library': 'Yes'}, container=Mock(type=NamedMock(real_name='96 well plate')))]),
        Mock(id='ai3', samples=[
            Mock(udf={'User Prepared Library': 'No'}, container=Mock(type=NamedMock(real_name='96 well plate')))])
    )


class TestAssignWorkflowReceiveSample(TestEPP):
    def setUp(self):
        self.patched_process = patch.object(
            AssignWorkflowPostReceiveSample,
            'process',
            new_callable=PropertyMock(return_value=Mock(all_inputs=fake_all_inputs))
        )
        self.patched_get_workflow_stage = patch(
            'scripts.assign_workflow_post_receive_sample.get_workflow_stage',
            return_value=Mock(uri='a_uri')
        )
        self.epp = AssignWorkflowPostReceiveSample(self.default_argv)

    def test_assign(self):
        with self.patched_get_workflow_stage as pws, self.patched_lims, self.patched_process:
            self.epp._run()

            pws.assert_has_calls((
                call(self.epp.lims, 'FluidX Receipt & Transfer EG 1.0 WF',
                     'FluidX Transfer From Rack Into Plate EG 1.0 ST'),
                call(self.epp.lims, 'User Prepared Library Receipt and Batch EG 1.0 WF',
                     'User Prepared Library Batch EG 1.0 ST'),
                call(self.epp.lims, 'PreSeqLab EG 6.0', 'Spectramax Picogreen EG 6.0')
            ))
            # first routing (tube transfer)
            route_args = self.epp.lims.route_artifacts.call_args_list[0]
            assert sorted([a.id for a in route_args[0][0]]) == ['ai1']
            assert self.epp.lims.route_artifacts.call_args[1] == {'stage_uri': 'a_uri'}

            # second routing (user prepared library)
            route_args = self.epp.lims.route_artifacts.call_args_list[1]
            assert sorted([a.id for a in route_args[0][0]]) == ['ai2']

            # third routing (plates to qc)
            route_args = self.epp.lims.route_artifacts.call_args_list[2]
            assert sorted([a.id for a in route_args[0][0]]) == ['ai3']
