from scripts.assign_sample_review import AssignWorkflowSampleReview
from tests.test_common import TestEPP, fake_artifact
from unittest.mock import Mock, patch, PropertyMock


def fake_all_outputs(unique=False, resolve=False):
    '''Return a list of mocked artifacts which contain sample which contain artifact ... Simple!'''
    return (
        Mock(samples=[Mock(artifact=fake_artifact('a1'), id='s1')], udf={"SR Useable": 'yes'}),
        Mock(samples=[Mock(artifact=fake_artifact('a2'), id='s2')],udf={"SR Useable":'yes'})
    )


class TestAssignWorkflowSampleReview(TestEPP):
    def setUp(self):
        self.patched_process = patch.object(
            AssignWorkflowSampleReview,
            'process',
            new_callable=PropertyMock(return_value=Mock(all_outputs=fake_all_outputs))
        )
        self.patched_lims = patch.object(AssignWorkflowSampleReview, 'lims', new_callable=PropertyMock)
        self.patched_get_workflow_stage = patch(
            'scripts.assign_sample_review.get_workflow_stage',
            return_value=Mock(uri='a_uri')
        )

        self.epp = AssignWorkflowSampleReview(
            'http://server:8080/a_step_uri',
            'a_user',
            'a_password',
            self.log_file
        )

    def test_assign(self):
        with self.patched_get_workflow_stage as pws, self.patched_lims, self.patched_process:
            self.epp._run()

            pws.assert_called_with(self.epp.lims, 'PostSeqLab EG 1.0 WF', 'Data Release Trigger EG 1.0 ST')
            observed = sorted([a.id for a in self.epp.lims.route_artifacts.call_args[0][0]])
            assert observed == ['a1', 'a2']
            assert self.epp.lims.route_artifacts.call_args[1] == {'stage_uri': 'a_uri'}

