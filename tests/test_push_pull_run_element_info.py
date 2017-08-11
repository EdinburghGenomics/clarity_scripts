from scripts.assign_workflow_user_library import AssignWorkflowUserPreparedLibrary
from scripts.push_pull_run_element_info import PullRunElementInfo
from tests.test_common import TestEPP, fake_artifact
from unittest.mock import Mock, patch, PropertyMock, call


def fake_all_output(unique=False, resolve=False):
    '''Return a list of mocked artifacts which contain sample which contain artifact ... Simple!'''
    return (
        Mock(id='ao1', samples=[Mock(artifact=fake_artifact(id='a1'), id='s1', udf={"Prep Workflow": "TruSeq PCR-Free DNA Sample Prep"})]),
        Mock(id='ao2', samples=[Mock(artifact=fake_artifact(id='a2'), id='s2', udf={"Prep Workflow": "TruSeq Nano DNA Sample Prep"})]),
    )


class TestPullRunElementInfo(TestEPP):
    def setUp(self):
        self.patched_samples = patch.object(
            PullRunElementInfo,
            'samples',
            new_callable=PropertyMock()
        )
        self.patched_lims = patch.object(PullRunElementInfo, 'lims', new_callable=PropertyMock)

        self.epp = PullRunElementInfo(
            'http://server:8080/a_step_uri',
            'a_user',
            'a_password',
            self.log_file
        )

    def test_pull(self):
        with self.patched_lims, self.patched_samples:
            self.epp.run()

