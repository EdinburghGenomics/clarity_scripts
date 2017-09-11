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
            pg.assert_called_with(self.epp.endpoint, match={'sample_id': 'a_sample'})

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

    def test_field_from_entity(self):
        entity = {'this': {'that': 'other'}}
        assert self.epp.field_from_entity(entity, 'this.that') == 'other'
        assert entity == {'this': {'that': 'other'}}  # not changed


class TestPullSampleInfo(TestPullRunElementInfo):
    epp_cls = p.PullSampleInfo
    fake_rest_entity = {
        'sample_id': 'a_sample',
        'user_sample_id': 'a_user_sample_id',
        'clean_yield_in_gb': 5,
        'clean_pc_q30': 70,
        'pc_mapped_reads': 75,
        'pc_duplicate_reads': 5,
        'coverage': {'mean': 30},
        'species_contamination': {
            'contaminant_unique_mapped': {'Homo sapiens': 70000, 'Thingius thingy': 501, 'Sus scrofa': 499}
        },
        'gender_match': 'Match',
        'genotype_match': 'Match',
        'sample_contamination': {'freemix': 0.1},
        'reviewed': 'pass',
        'review_comments': 'alright',
        'review_date': '12_02_2017_12:43:24'
    }
    expected_udfs = {
        'SR Yield (Gb)': 5,
        'SR %Q30': 70,
        'SR % Mapped': 75,
        'SR % Duplicates': 5,
        'SR Mean Coverage': 30,
        'SR Species Found': 'Homo sapiens, Thingius thingy',
        'SR Sex Check Match': 'Match',
        'SR Genotyping Match': 'Match',
        'SR Freemix': 0.1,
        'SR Review Comments': 'alright',
        'SR Review Status': 'pass',
        'SR Review Date': '2017-02-12',
        'SR Useable': 'yes',
        'SR Useable Comments': 'AR: Review passed'
    }

    def test_assess_sample(self):
        def patch_output_artifact(output_artifacts):
            return patch.object(self.epp_cls, 'output_artifacts_per_sample', return_value=output_artifacts)

        sample = NamedMock(real_name='a_sample')
        patched_output_artifacts_per_sample = patch_output_artifact([
            Mock(spec=Artifact, udf={'SR Review Status': 'pass'}),
            Mock(spec=Artifact, udf={'SR Review Status': 'fail'}),
        ])
        with patched_output_artifacts_per_sample as poa:
            self.epp.assess_sample(sample)
            assert poa.return_value[0].udf['SR Useable'] == 'yes'
            assert poa.return_value[0].udf['SR Useable Comments'] == 'AR: Review passed'

            assert poa.return_value[1].udf['SR Useable'] == 'no'
            assert poa.return_value[1].udf['SR Useable Comments'] == 'AR: Review failed'

    def test_field_from_entity(self):
        obs = self.epp.field_from_entity(self.fake_rest_entity, 'species_contamination')
        assert obs == 'Homo sapiens, Thingius thingy'


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
            return_value=[Mock(spec=Artifact, udf=self.fake_artifact_udfs, samples=[NamedMock(real_name='a_sample')])]
        )

    def test_push(self):
        with self.patched_lims, self.patched_samples, self.patched_get_docs as pg, self.patched_patch as prp, \
                self.patched_process, self.patched_output_artifacts_per_sample:
            self.epp.run()

            assert pg.call_count == 1
            pg.assert_called_with(self.epp.endpoint, where={'sample_id': 'a_sample'})

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
    fake_artifact_udfs = {'SR Useable': 'no', 'SR Useable Comments': 'too bad'}
    fake_rest_entity = {
        'sample_id': 'a_sample',
        'reviewed': 'pass',
        'review_comments': 'alright',
        'review_date': '12_02_2017_12:43:24'
    }
