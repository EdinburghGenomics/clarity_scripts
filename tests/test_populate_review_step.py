from pyclarity_lims.entities import Artifact
from scripts import populate_review_step as p
from tests.test_common import TestEPP, NamedMock
from unittest.mock import Mock, patch, PropertyMock, call


class TestPopulator(TestEPP):
    fake_rest_entity = None

    def setUp(self):
        self.epp = p.StepPopulator(self.default_argv)

    @property
    def patched_samples(self):
        return patch.object(
            self.epp.__class__,
            'samples',
            new_callable=PropertyMock(
                return_value=[NamedMock(real_name='a_sample', udf={'Required Yield (Gb)': 95, 'Coverage (X)': 30})]
            )
        )

    @property
    def patched_get_docs(self):
        return patch.object(self.epp.__class__, 'get_documents', return_value=[self.fake_rest_entity])


class TestPullRunElementInfo(TestPopulator):
    fake_rest_entity = {
        'aggregated': {
            'clean_yield_in_gb': 20,
            'clean_yield_q30_in_gb': 15,
            'clean_pc_q30': 75,
            'pc_adaptor': 1.2
        },
        'run_element_id': 'id',
        'passing_filter_reads': 120000000,
        'lane_pc_optical_dups': 10,
        'reviewed': 'pass',
        'review_comments': 'alright',
        'review_date': '12_02_2107_12:43:24',
    }
    expected_udfs = {
        'RE Id': 'id',
        'RE Nb Reads': 120000000,
        'RE Yield': 20,
        'RE Yield Q30': 15,
        'RE Coverage': 34.2,
        'RE %Q30': 75,
        'RE Estimated Duplicate Rate': 10,
        'RE %Adapter': 1.2,
        'RE Review status': 'pass',
        'RE Review Comment': 'alright',
        'RE Review date': '2107-02-12',
        'RE Useable': 'yes',
        'RE Useable Comment': 'AR: Good yield'
    }

    def setUp(self):
        self.epp = p.PullRunElementInfo(self.default_argv)

    def test_pull(self):
        patched_output_artifacts_per_sample = patch.object(
            self.epp.__class__,
            'output_artifacts_per_sample',
            return_value=[Mock(spec=Artifact, udf={'RE Coverage': 34.2}, samples=[NamedMock(real_name='a_sample')])]
        )

        with self.patched_lims as pl, self.patched_samples, self.patched_get_docs as pg, \
                patched_output_artifacts_per_sample as poa:
            self.epp.run()

            assert pg.call_count == 3
            assert pg.call_args_list == [call('run_elements', where={'sample_id': 'a_sample'}),
                                         call('samples', where={'sample_id': 'a_sample'}),
                                         call('samples', where={'sample_id': 'a_sample'})]

            # Check that the udfs have been added
            assert dict(poa.return_value[0].udf) == self.expected_udfs

            # check that the artifacts have been uploaded
            pl.put_batch.assert_called_once_with({poa.return_value[0]})

    def test_assess_sample(self):
        patched_output_artifacts_per_sample = patch.object(self.epp.__class__, 'output_artifacts_per_sample')
        sample = NamedMock(real_name='a_sample', udf={'Required Yield (Gb)': 95, 'Coverage (X)': 30})

        with self.patched_get_docs, patched_output_artifacts_per_sample as poa:
            poa.return_value = [
                Mock(spec=Artifact, udf={'RE Yield': 115, 'RE %Q30': 75, 'RE Review status': 'pass', 'RE Coverage': 35.2}),
                Mock(spec=Artifact, udf={'RE Yield': 95, 'RE %Q30': 85, 'RE Review status': 'pass', 'RE Coverage': 36.7}),
                Mock(spec=Artifact, udf={'RE Yield': 15, 'RE %Q30': 70, 'RE Review status': 'fail', 'RE Coverage': 34.1}),
            ]
            self.epp.assess_sample(sample)
            assert poa.return_value[0].udf['RE Useable'] == 'no'
            assert poa.return_value[0].udf['RE Useable Comment'] == 'AR: Too much good yield'
            assert poa.return_value[1].udf['RE Useable'] == 'yes'
            assert poa.return_value[1].udf['RE Useable Comment'] == 'AR: Good yield'
            assert poa.return_value[2].udf['RE Useable'] == 'no'
            assert poa.return_value[2].udf['RE Useable Comment'] == 'AR: Failed and not needed'

            poa.reset_mock()
            poa.return_value = [
                Mock(spec=Artifact, udf={'RE Yield': 115, 'RE %Q30': 85, 'RE Review status': 'pass', 'RE Coverage': 35.2}),
                Mock(spec=Artifact, udf={'RE Yield': 15, 'RE %Q30': 70, 'RE Review status': 'fail', 'RE Coverage': 33.6}),
            ]
            self.epp.assess_sample(sample)
            assert poa.return_value[0].udf['RE Useable'] == 'yes'
            assert poa.return_value[0].udf['RE Useable Comment'] == 'AR: Good yield'
            assert poa.return_value[1].udf['RE Useable'] == 'no'
            assert poa.return_value[1].udf['RE Useable Comment'] == 'AR: Failed and not needed'

            poa.reset_mock()
            poa.return_value = [
                Mock(spec=Artifact, udf={'RE Yield': 115, 'RE %Q30': 85, 'RE Review status': 'pass', 'RE Coverage': 35.2}),
                Mock(spec=Artifact, udf={'RE Yield': 15, 'RE %Q30': 70, 'RE Review status': 'fail', 'RE Coverage': 33.6}),
            ]
            with patch.object(self.epp.__class__, 'delivered', return_value=True):
                self.epp.assess_sample(sample)
                assert poa.return_value[0].udf['RE Useable'] == 'no'
                assert poa.return_value[0].udf['RE Useable Comment'] == 'AR: Delivered'
                assert poa.return_value[1].udf['RE Useable'] == 'no'
                assert poa.return_value[1].udf['RE Useable Comment'] == 'AR: Delivered'

            with patch.object(self.epp.__class__, 'processed', return_value=True):
                self.epp.assess_sample(sample)
                assert poa.return_value[0].udf['RE Useable'] == 'no'
                assert poa.return_value[0].udf['RE Useable Comment'] == 'AR: Sample already processed'
                assert poa.return_value[1].udf['RE Useable'] == 'no'
                assert poa.return_value[1].udf['RE Useable Comment'] == 'AR: Sample already processed'

    def test_field_from_entity(self):
        entity = {'this': {'that': 'other'}}
        assert self.epp.field_from_entity(entity, 'this.that') == 'other'
        assert entity == {'this': {'that': 'other'}}  # not changed


class TestPullSampleInfo(TestPopulator):
    fake_rest_entity = {
        'sample_id': 'a_sample',
        'user_sample_id': 'a_user_sample_id',
        'clean_yield_in_gb': 5,
        'aggregated': {
            'clean_pc_q30': 70,
            'pc_mapped_reads': 75,
            'pc_duplicate_reads': 5,
            'mean_coverage': 30,
            'sex_match': 'Match',
            'genotype_match': 'Match',
            'matching_species': ['Homo sapiens', 'Thingius thingy'],
        },
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

    def setUp(self):
        self.epp = p.PullSampleInfo(self.default_argv)

    def test_assess_sample(self):
        patched_output_artifacts_per_sample = patch.object(
            self.epp.__class__,
            'output_artifacts_per_sample',
            return_value=[
                Mock(spec=Artifact, udf={'SR Review Status': 'pass'}),
                Mock(spec=Artifact, udf={'SR Review Status': 'fail'}),
            ]
        )
        fake_sample = NamedMock(real_name='a_sample')
        with patched_output_artifacts_per_sample as poa:
            self.epp.assess_sample(fake_sample)
            assert poa.return_value[0].udf['SR Useable'] == 'yes'
            assert poa.return_value[0].udf['SR Useable Comments'] == 'AR: Review passed'
            assert poa.return_value[1].udf['SR Useable'] == 'no'
            assert poa.return_value[1].udf['SR Useable Comments'] == 'AR: Review failed'

    def test_field_from_entity(self):
        obs = self.epp.field_from_entity(self.fake_rest_entity, 'aggregated.matching_species')
        assert obs == 'Homo sapiens, Thingius thingy'


class TestPushRunElementInfo(TestPopulator):
    patched_process = patch.object(p.StepEPP, 'process', new=Mock(id='a_process_id'))
    fake_artifact_udfs = {'RE Id': 'id', 'RE Useable': 'no', 'RE Useable Comment': 'too bad'}
    fake_rest_entity = {
        'run_element_id': 'id',
        'reviewed': 'pass',
        'review_comments': 'alright',
        'review_date': '12_02_2107_12:43:24'
    }

    @property
    def patched_output_artifacts_per_sample(self):
        return patch.object(
            self.epp.__class__,
            'output_artifacts_per_sample',
            return_value=[Mock(spec=Artifact, udf=self.fake_artifact_udfs, samples=[NamedMock(real_name='a_sample')])]
        )

    def setUp(self):
        self.epp = p.PushRunElementInfo(self.default_argv)

    def test_push(self):
        with self.patched_lims, self.patched_samples, self.patched_get_docs as pg, \
                patch('egcg_core.rest_communication.patch_entry') as prp, \
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
    fake_artifact_udfs = {'SR Useable': 'no', 'SR Useable Comments': 'too bad'}
    fake_rest_entity = {
        'sample_id': 'a_sample',
        'reviewed': 'pass',
        'review_comments': 'alright',
        'review_date': '12_02_2017_12:43:24'
    }

    def setUp(self):
        self.epp = p.PushSampleInfo(self.default_argv)
