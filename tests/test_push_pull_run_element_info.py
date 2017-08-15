from pyclarity_lims.entities import Artifact

from scripts.push_pull_run_element_info import PullRunElementInfo, PushRunElementInfo, reporting_app_date_format
from tests.test_common import TestEPP, fake_artifact, NamedMock
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
            new_callable=PropertyMock(return_value=[NamedMock(real_name='sample1')])
        )
        self.patched_lims = patch.object(PullRunElementInfo, 'lims', new_callable=PropertyMock)
        run_element = {
            'run_element_id':'id',
            'passing_filter_reads': 120000000,
            'clean_yield_in_gb': 20,
            'clean_yield_q30_in_gb': 15,
            'clean_pc_q30': 75,
            'lane_pc_optic  al_dups': 10,
            'pc_adapter': 1.2,
            'reviewed': 'pass',
            'review_comments': 'alright',
            'review_date': '12_02_2107_12:43:24'
        }
        self.patched_rest_comm = patch('egcg_core.rest_communication.get_documents', return_value=[run_element])

        self.patched_output_artifacts_per_sample = patch.object(
            PullRunElementInfo,
            'output_artifacts_per_sample',
            return_value=[Mock(spec=Artifact, udf={})]
        )
        self.epp = PullRunElementInfo(
            'http://server:8080/a_step_uri',
            'a_user',
            'a_password',
            self.log_file
        )

    def test_pull(self):
        with self.patched_lims as pl, self.patched_samples as ps, \
                self.patched_rest_comm as pr, self.patched_output_artifacts_per_sample as poa:
            self.epp.run()
            #Check that the udfs have been added
            expected_udfs = {
                'RE Yield Q30': 15,
                'RE Review Comment': 'alright',
                'RE %Q30': 75,
                'RE Review status': 'pass',
                'RE Review date': '2107-02-12',
                'RE Yield': 20,
                'RE Nb Reads': 120000000,
                'RE Id': 'id',
                'RE %Adapter': 1.2
            }
            assert dict(poa.return_value[0].udf) == expected_udfs

            # check that the artifacts have been uploaded
            pl().put_batch.assert_called_once_with({poa.return_value[0]})



class TestPushRunElementInfo(TestEPP):
    def setUp(self):
        self.patched_samples = patch.object(
            PushRunElementInfo,
            'samples',
            new_callable=PropertyMock(return_value=[NamedMock(real_name='sample1')])
        )
        self.patched_process = patch.object(
            PushRunElementInfo,
            'process',
            new_callable=PropertyMock(return_value=Mock(id='processid'))
        )
        self.patched_lims = patch.object(PushRunElementInfo, 'lims', new_callable=PropertyMock)
        run_element = {
            'run_element_id':'id',
            'reviewed': 'pass',
            'review_comments': 'alright',
            'review_date': '12_02_2107_12:43:24'
        }
        self.patched_rest_get_doc = patch('egcg_core.rest_communication.get_documents', return_value=[run_element])
        self.patched_rest_patch = patch('egcg_core.rest_communication.patch_entry')

        self.patched_output_artifacts_per_sample = patch.object(
            PushRunElementInfo,
            'output_artifacts_per_sample',
            return_value=[Mock(spec=Artifact, udf={'RE Id': 'id', 'RE Useable': 'no', 'RE Useable Comment': 'too bad'})]
        )
        self.epp = PushRunElementInfo(
            'http://server:8080/a_step_uri',
            'a_user',
            'a_password',
            self.log_file
        )


    def test_push(self):
        with self.patched_lims as pl, self.patched_samples as ps, \
                self.patched_rest_get_doc as prgd, self.patched_rest_patch as prp, \
                self.patched_process as pp, \
                self.patched_output_artifacts_per_sample as poa:
            self.epp.run()
            # Check that the run element was updated
            prp.assert_any_call_with(
                'run_elements',
                {
                    'useable': 'no',
                    'useable_comments': 'too bad',
                    'useable_date': self.epp.now.strftime(reporting_app_date_format)
                },
                'run_element_id',
                'id'
            )

            # Check that the action was updated
            prp.assert_called_with(
                'actions',
                {'date_finished': self.epp.now.strftime(reporting_app_date_format) },
                'action_id',
                'lims_processid'
            )
