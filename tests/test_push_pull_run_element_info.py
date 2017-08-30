from pyclarity_lims.entities import Artifact
from scripts import push_pull_run_element_info as p
from tests.test_common import TestEPP, NamedMock
from unittest.mock import Mock, patch, PropertyMock


class TestPopulator(TestEPP):
    epp_cls = p.StepPopulator
    fake_rest_entity = None

    def setUp(self):
        self.patched_samples = patch.object(
            self.epp_cls,
            'samples',
            new_callable=PropertyMock(
                return_value=[NamedMock(real_name='a_sample', udf={'Yield for Quoted Coverage (Gb)': 95})]
            )
        )
        self.patched_lims = patch.object(self.epp_cls, 'lims', new_callable=PropertyMock)
        self.patched_get_docs = patch.object(self.epp_cls, 'get_documents', return_value=[self.fake_rest_entity])
        self.patched_output_artifacts_per_sample = patch.object(
            self.epp_cls,
            'output_artifacts_per_sample',
            return_value=[Mock(spec=Artifact, udf={})]
        )

        self.epp = self.epp_cls('http://server:8080/a_step_uri', 'a_user', 'a_password', self.log_file)


class TestPullRunElementInfo(TestPopulator):
    epp_cls = p.PullRunElementInfo
    fake_rest_entity = {
        'run_element_id': 'id',
        'passing_filter_reads': 120000000,
        'clean_yield_in_gb': 20,
        'clean_yield_q30_in_gb': 15,
        'clean_pc_q30': 75,
        'lane_pc_optical_dups': 10,
        'pc_adapter': 1.2,
        'reviewed': 'pass',
        'review_comments': 'alright',
        'review_date': '12_02_2107_12:43:24'
    }
    expected_udfs = {
        'RE Id': 'id',
        'RE Nb Reads': 120000000,
        'RE Yield': 20,
        'RE Yield Q30': 15,
        'RE %Q30': 75,
        'RE Estimated Duplicate Rate': 10,
        'RE %Adapter': 1.2,
        'RE Review status': 'pass',
        'RE Review Comment': 'alright',
        'RE Review date': '2107-02-12'
    }

    def test_pull(self):
        with self.patched_lims as pl, self.patched_samples, self.patched_get_docs as pg, \
                self.patched_output_artifacts_per_sample as poa:
            self.epp.run()

            assert pg.call_count == 1

            # Check that the udfs have been added
            assert dict(poa.return_value[0].udf) == self.expected_udfs

            # check that the artifacts have been uploaded
            pl().put_batch.assert_called_once_with({poa.return_value[0]})

    def test_assess_sample(self):
        def patch_output_artifact(output_artifacts):
            return patch.object(self.epp_cls, 'output_artifacts_per_sample', return_value=output_artifacts)

        sample = NamedMock(real_name='a_sample', udf={'Yield for Quoted Coverage (Gb)': 95})
        patched_output_artifacts_per_sample = patch_output_artifact([
            Mock(spec=Artifact, udf={'RE Yield Q30': 115, 'RE %Q30': 75, 'RE Review status': 'pass'}),
            Mock(spec=Artifact, udf={'RE Yield Q30': 95, 'RE %Q30': 85, 'RE Review status': 'pass'}),
            Mock(spec=Artifact, udf={'RE Yield Q30': 15, 'RE %Q30': 70, 'RE Review status': 'fail'}),
        ])
        with patched_output_artifacts_per_sample as poa:
            self.epp.assess_sample(sample)
            assert poa.return_value[0].udf['RE Useable'] == 'no'
            assert poa.return_value[0].udf['RE Useable Comment'] == 'AR: To much good yield'

            assert poa.return_value[1].udf['RE Useable'] == 'yes'
            assert poa.return_value[1].udf['RE Useable Comment'] == 'AR: Good yield'

            assert poa.return_value[2].udf['RE Useable'] == 'no'
            assert poa.return_value[2].udf['RE Useable Comment'] == 'AR: Failed and not needed'

        patched_output_artifacts_per_sample = patch_output_artifact([
            Mock(spec=Artifact, udf={'RE Yield Q30': 115, 'RE %Q30': 85, 'RE Review status': 'pass'}),
            Mock(spec=Artifact, udf={'RE Yield Q30': 15, 'RE %Q30': 70, 'RE Review status': 'fail'}),
        ])
        with patched_output_artifacts_per_sample as poa:
            self.epp.assess_sample(sample)
            assert poa.return_value[0].udf['RE Useable'] == 'yes'
            assert poa.return_value[0].udf['RE Useable Comment'] == 'AR: Good yield'

            assert poa.return_value[1].udf['RE Useable'] == 'no'
            assert poa.return_value[1].udf['RE Useable Comment'] == 'AR: Failed and not needed'


class TestPullSampleInfo(TestPullRunElementInfo):
    epp_cls = p.PullSampleInfo
    fake_rest_entity = {
        'sample_id': 'a_sample',
        'user_sample_id': 'a_user_sample_id',
        'yield': 5,
        'qc_q30': 70,
        'pc_mapped': 75,
        'pc_duplicates': 5,
        'mean_coverage': 30,
        'species_found': 'Thingius thingy',
        'gender_match': 'Match',
        'genotype_match': 'Match',
        'freemix': 0.1,
        'reviewed': 'pass',
        'review_comments': 'alright',
        'review_date': '12_02_2017_12:43:24'
    }
    expected_udfs = {
        'Sample ID': 'a_sample',
        'User Sample ID': 'a_user_sample_id',
        'Sample Yield': 5,
        'Sample %Q30': 70,
        'Sample % Mapped': 75,
        'Sample % Duplicates': 5,
        'Sample Mean Coverage': 30,
        'Sample Species Found': 'Thingius thingy',
        'Sample Sex Check Match': 'Match',
        'Sample Genotype Match': 'Match',
        'Sample Freemix': 0.1,
        'Sample Review Comment': 'alright',
        'Sample Review status': 'pass',
        'Sample Review date': '2017-02-12',
        'Sample Useable': 'yes',
        'Sample Useable Comment': 'AR: Review passed'
    }

    def test_assess_sample(self):
        def patch_output_artifact(output_artifacts):
            return patch.object(self.epp_cls, 'output_artifacts_per_sample', return_value=output_artifacts)

        sample = NamedMock(real_name='a_sample')
        patched_output_artifacts_per_sample = patch_output_artifact([
            Mock(spec=Artifact, udf={'Sample Review status': 'pass'}),
            Mock(spec=Artifact, udf={'Sample Review status': 'fail'}),
        ])
        with patched_output_artifacts_per_sample as poa:
            self.epp.assess_sample(sample)
            assert poa.return_value[0].udf['Sample Useable'] == 'yes'
            assert poa.return_value[0].udf['Sample Useable Comment'] == 'AR: Review passed'

            assert poa.return_value[1].udf['Sample Useable'] == 'no'
            assert poa.return_value[1].udf['Sample Useable Comment'] == 'AR: Review failed'


class TestPushRunElementInfo(TestPopulator):
    epp_cls = p.PushRunElementInfo
    fake_artifact_udfs = {'RE Id': 'id', 'RE Useable': 'no', 'RE Useable Comment': 'too bad'}
    fake_rest_entity = {
        'run_element_id': 'id',
        'reviewed': 'pass',
        'review_comments': 'alright',
        'review_date': '12_02_2107_12:43:24'
    }

    def setUp(self):
        super().setUp()
        self.patched_patch = patch('egcg_core.rest_communication.patch_entry')
        self.patched_output_artifacts_per_sample = patch.object(
            self.epp_cls,
            'output_artifacts_per_sample',
            return_value=[Mock(spec=Artifact, udf=self.fake_artifact_udfs)]
        )

    def test_push(self):
        with self.patched_lims, self.patched_samples, self.patched_get_docs as pg, self.patched_patch as prp, \
                self.patched_process, self.patched_output_artifacts_per_sample:
            self.epp.run()

            assert pg.call_count == 1

            # Check that the run element was updated
            prp.assert_any_call(
                self.epp.endpoint,
                {'useable': 'no', 'useable_comments': 'too bad', 'useable_date': self.epp.current_time},
                self.epp.api_id_field,
                self.fake_rest_entity[self.epp.api_id_field]
            )

            # Check that the action was updated
            prp.assert_called_with('actions', {'date_finished': self.epp.current_time}, 'action_id', 'lims_a_process_id')


class TestPushSampleInfo(TestPushRunElementInfo):
    epp_cls = p.PushSampleInfo
    fake_artifact_udfs = {'Sample ID': 'a_sample', 'Sample Useable': 'no', 'Sample Useable Comment': 'too bad'}
    fake_rest_entity = {
        'sample_id': 'a_sample',
        'reviewed': 'pass',
        'review_comments': 'alright',
        'review_date': '12_02_2017_12:43:24'
    }
