from scripts.assign_workflow_user_library import AssignWorkflowUserPreparedLibrary
from tests.test_common import TestEPP, fake_artifact
from unittest.mock import Mock, patch, PropertyMock, call


def fake_all_output(unique=False, resolve=False):
    """Return a list of mocked artifacts which contain samples which contain artifacts... Simple!"""
    return (
        Mock(id='ao1', samples=[Mock(artifact=fake_artifact('a1'), id='s1', udf={'SSQC Result': ''})]),
        Mock(id='ao2', samples=[Mock(artifact=fake_artifact('a2'), id='s2', udf={'SSQC Result': ''})])
    )


class TestAssignWorkflowUserPreparedLibrary(TestEPP):
    def setUp(self):
        self.patched_process = patch.object(
            AssignWorkflowUserPreparedLibrary,
            'process',
            new_callable=PropertyMock(return_value=Mock(all_outputs=fake_all_output))
        )
        self.patched_lims = patch.object(AssignWorkflowUserPreparedLibrary, 'lims', new_callable=PropertyMock)
        self.patched_get_workflow_stage = patch(
            'scripts.assign_workflow_user_library.get_workflow_stage',
            return_value=Mock(uri='a_uri')
        )

        self.epp = AssignWorkflowUserPreparedLibrary(self.default_argv)

    def test_assign(self):
        with self.patched_get_workflow_stage as pws, self.patched_lims, self.patched_process:
            self.epp._run()

            pws.assert_has_calls((
                call(self.epp.lims, 'TruSeq Nano DNA Sample Prep', 'SEMI-AUTOMATED - Make and Read qPCR Quant'),
            ))
            # test that sample is routed to SEMI-AUTOMATED - Make and Read qPCR and that sample UDF SSQC Result
            # is updated to "Passed
            assert self.epp.output_artifacts[0].samples[0].udf['SSQC Result'] == 'Passed'
            route_args = self.epp.lims.route_artifacts.call_args_list[0]
            assert [a.id for a in route_args[0][0]] == ['ao1', 'ao2']
            assert self.epp.lims.route_artifacts.call_args[1] == {'stage_uri': 'a_uri'}
