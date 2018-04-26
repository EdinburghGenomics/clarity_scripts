from scripts.assign_workflow_finance import AssignWorkflowFinance
from tests.test_common import TestEPP, fake_artifact
from unittest.mock import Mock, patch, PropertyMock


def fake_all_inputs(unique=False, resolve=False):
    '''Return a list of mocked artifacts which contain sample which contain artifact ... Simple!'''
    return (
        Mock(samples=[Mock(artifact=fake_artifact('a1'), id='s1')]),
        Mock(samples=[Mock(artifact=fake_artifact('a2'), id='s2')])

    )


class TestAssignWorkflowSampleReview(TestEPP):
    def setUp(self):
        self.patched_process = patch.object(
            AssignWorkflowFinance,
            'process',
            new_callable=PropertyMock(return_value=Mock(all_inputs=fake_all_inputs))
        )
        self.patched_lims = patch.object(AssignWorkflowFinance, 'lims', new_callable=PropertyMock)
        self.patched_get_workflow_stage = patch(
            'scripts.assign_workflow_finance.get_workflow_stage',
            return_value=Mock(uri='a_uri')
        )

        self.epp = AssignWorkflowFinance(
            'http://server:8080/a_step_uri',
            'a_user',
            'a_password',
            self.log_file
        )

    def test_assign(self):
        with self.patched_get_workflow_stage as pws, self.patched_lims, self.patched_process:
            self.epp._run()

            pws.assert_called_with(self.epp.lims, "Finance - Invoicing EG 1.0", "Finance - Invoice To Be Sent")
            observed = sorted([a.id for a in self.epp.lims.route_artifacts.call_args[0][0]])
            assert observed == ['a1','a2']
            assert self.epp.lims.route_artifacts.call_args[1] == {'stage_uri': 'a_uri'}

