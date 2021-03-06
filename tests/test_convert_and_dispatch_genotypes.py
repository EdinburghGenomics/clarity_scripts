import pytest
from os.path import join
from EPPs.common import StepEPP
from tests.test_common import TestCommon, TestEPP, NamedMock
from unittest.mock import Mock, patch, PropertyMock
from scripts.convert_and_dispatch_genotypes import GenotypeConversion, UploadVcfToSamples


class TestGenotypeConversion(TestCommon):
    small_reference_fai = join(TestCommon.assets, 'genotype_32_SNPs_genome_600bp.fa.fai')
    test_records = {
        'id1': {'test_sample': '0/1', 'SNP': ['chr2', '120', 'id1', 'T', 'C', '.', '.', '.', 'GT']},
        'id2': {'test_sample': '1/1', 'SNP': ['chr1', '601', 'id2', 'C', 'A', '.', '.', '.', 'GT']},
        'id3': {'test_sample': '1/1', 'SNP': ['chr2', '72', 'id3', 'C', 'T', '.', '.', '.', 'GT']},
        'id4': {'test_sample': '0/1', 'SNP': ['chr1', '200', 'id4', 'A', 'G', '.', '.', '.', 'GT']},
    }

    def setUp(self):
        self.geno_conversion = GenotypeConversion(
            [open(self.genotype_quantstudio)], self.small_reference_fai, flank_length=600
        )

    def test_generate_vcf(self):
        # header_lines = ['##header line1', '##header line2']
        # snp_ids = ['id4', 'id2', 'id3', 'id1']
        # TODO: make assertions on what header lines, snp IDs, etc. have been written
        path = join(self.assets, 'test_generate')
        vcf_file = path + '.vcf'
        assert self.geno_conversion.generate_vcf('V0001P001C01', new_name=path) == vcf_file
        with open(vcf_file) as f:
            assert 26 == len([l for l in f.readlines() if not l.startswith('#')])

    def test_get_genotype_from_call(self):
        genotype = self.geno_conversion.get_genotype_from_call('A', 'T', 'Both', )
        assert genotype == '0/1'
        genotype = self.geno_conversion.get_genotype_from_call('A', 'T', 'Undefined')
        assert genotype == './.'
        with pytest.raises(ValueError) as e:
            self.geno_conversion.get_genotype_from_call('G', 'T', 'A')
            assert str(e) == 'Call G does not match any of the alleles (ref:T, alt:A)'

    def test_vcf_header_from_ref_length(self):
        expected_vcf_headers = ['##contig=<ID=test1,length=48>', '##contig=<ID=test2,length=656>',
                                '##contig=<ID=test3,length=35>', '##contig=<ID=test4,length=10>']

        reference_length = [('test1', '48'), ('test2', '656'), ('test3', '35'), ('test4', '10')]
        observed_vcf_headers = self.geno_conversion.vcf_header_from_ref_length(reference_length)
        assert expected_vcf_headers == observed_vcf_headers

    def test_order_from_fai(self):
        reference_length = [('chr1', '2000'), ('chr2', '2000')]
        expected_records = ['id4', 'id2', 'id3', 'id1']
        assert self.geno_conversion.order_from_fai(self.test_records, reference_length) == expected_records

    def test_parse_genome_fai(self):
        refence_length = self.geno_conversion._parse_genome_fai()
        expected_ref_length = [
            (i, '1201') for i in (
                'C___2728408_10', 'C___1563023_10', 'C__15935210_10', 'C__33211212_10', 'C___3227711_10',
                'C__30044763_10', 'C__11821218_10', 'C___1670459_10', 'C__29619553_10', 'C___1007630_10',
                'C__26546714_10', 'C___7421900_10', 'C__27402849_10', 'C___2953330_10', 'C__16205730_10',
                'C___8850710_10', 'C___1801627_20', 'C___7431888_10', 'C___1250735_20', 'C___1902433_10',
                'C__31386842_10', 'C__26524789_10', 'C___8924366_10', 'C_____43852_10', 'C__11522992_10',
                'C__10076371_10', 'C___7457509_10', 'C___1122315_10', 'C__11710129_10', 'C___1027548_20',
                'C___8938211_20', 'C___1083232_10')
        ]
        assert refence_length == expected_ref_length

    def test_parse_quantstudio_flex_genotype(self):
        assert self.geno_conversion.sample_names == {'V0001P001C01', 'V0001P001A01'}
        assert len(self.geno_conversion.all_records) == 26
        assert self.geno_conversion.all_records['rs1567612'] == {
            'SNP': ['C___7457509_10', '601', 'rs1567612', 'G', 'A', '.', '.', '.', 'GT'],
            'V0001P001A01': './.', 'V0001P001C01': '0/1'
        }
        assert self.geno_conversion.all_records['rs6598531'] == {
            'SNP': ['C__11522992_10', '601', 'rs6598531', 'T', 'G', '.', '.', '.', 'GT'],
            'V0001P001A01': './.', 'V0001P001C01': './.'
        }

    def test_find_field(self):
        observed_fieldnames = ('__this__', 'that', 'OTHER')
        valid_this_fieldnames = ('this', 'THIS', '__this__')
        valid_that_fieldnames = ('that', 'THAT', '__that__')
        valid_other_fieldnames = ('other', 'OTHER', '__other__')

        find = self.geno_conversion._find_field
        assert find(valid_this_fieldnames, observed_fieldnames) == '__this__'
        assert find(valid_that_fieldnames, observed_fieldnames) == 'that'
        assert find(valid_other_fieldnames, observed_fieldnames) == 'OTHER'


class TestUploadVcfToSamples(TestEPP):
    def setUp(self):
        self.epp = UploadVcfToSamples(self.default_argv + ['--input_genotypes', self.genotype_quantstudio])
        self.lims_sample1 = NamedMock(real_name='V0001P001A01', udf={})
        self.lims_sample2 = NamedMock(real_name='V0001P001C01', udf={})
        fake_all_inputs = Mock(
            return_value=[
                Mock(samples=[self.lims_sample1]),
                Mock(samples=[self.lims_sample2])
            ]
        )
        # all output artifacts
        self.outputs = {}

        def fake_find_output_art(inart):
            if inart.samples[0] not in self.outputs:
                self.outputs[inart.samples[0]] = Mock(samples=inart.samples, udf={})
            return [self.outputs[inart.samples[0]]]

        self.patched_process = patch.object(StepEPP, 'process', new_callable=PropertyMock(
            return_value=Mock(all_inputs=fake_all_inputs)
        ))
        self.patched_find_output_art = patch.object(UploadVcfToSamples, '_find_output_art',
                                                    side_effect=fake_find_output_art)

    def test_upload_first_time(self):
        patched_log = patch.object(UploadVcfToSamples, 'info')
        patched_generate_vcf = patch.object(GenotypeConversion, 'generate_vcf', return_value='uploaded_file')
        patched_remove = patch('scripts.convert_and_dispatch_genotypes.remove')

        exp_log_msgs = (
            ('Matching %s samples from file against %s artifacts', 2, 2),
            ('Matching %s', 'V0001P001A01'),
            ('Matching %s', 'V0001P001C01'),
            ('Matched and uploaded %s artifacts against %s genotype results', 2, 2),
            ('%s artifacts did not match', 0),
            ('%s genotyping results were not used', 0)
        )

        with patched_log as p, patched_generate_vcf, patched_remove, self.patched_lims as mlims, self.patched_process,\
                self.patched_find_output_art:
            mlims.upload_new_file.return_value = Mock(id='file_id')
            self.epp._run()

            for m in exp_log_msgs:
                p.assert_any_call(*m)
            mlims.upload_new_file.assert_any_call(self.lims_sample1, 'uploaded_file')
            mlims.upload_new_file.assert_called_with(self.lims_sample2, 'uploaded_file')
            self.lims_sample1.put.assert_called_once_with()
            self.lims_sample2.put.assert_called_once_with()
            assert self.lims_sample1.udf == {
                'QuantStudio Data Import Completed #': 1,
                'Number of Calls (Best Run)': 6,
                'Genotyping results file id': 'file_id'
            }
            assert self.outputs[self.lims_sample1].udf == {'Number of Calls (This Run)': 6}
            assert self.lims_sample2.udf == {
                'QuantStudio Data Import Completed #': 1,
                'Number of Calls (Best Run)': 22,
                'Genotyping results file id': 'file_id'
            }
            assert self.outputs[self.lims_sample2].udf == {'Number of Calls (This Run)': 22}

    def test_upload_second_time(self):
        patched_log = patch.object(UploadVcfToSamples, 'info')
        patched_generate_vcf = patch.object(GenotypeConversion, 'generate_vcf', return_value='uploaded_file')
        patched_remove = patch('scripts.convert_and_dispatch_genotypes.remove')

        with patched_log, patched_generate_vcf, patched_remove, self.patched_lims as mlims, self.patched_process, \
                self.patched_find_output_art:
            self.lims_sample1.udf = {
                'QuantStudio Data Import Completed #': 1,
                'Number of Calls (Best Run)': 12,
                'Genotyping results file id': 'old_file_id'
            }
            self.lims_sample2.udf = {
                'QuantStudio Data Import Completed #': 1,
                'Number of Calls (Best Run)': 0,
                'Genotyping results file id': 'old_file_id'
            }
            mlims.upload_new_file.return_value = Mock(id='file_id')
            self.epp._run()
            assert self.lims_sample1.udf == {
                'QuantStudio Data Import Completed #': 2,
                'Number of Calls (Best Run)': 12,
                'Genotyping results file id': 'old_file_id'
            }
            assert self.outputs[self.lims_sample1].udf == {'Number of Calls (This Run)': 6}
            self.lims_sample1.put.assert_called_once()

            assert self.lims_sample2.udf == {
                'QuantStudio Data Import Completed #': 2,
                'Number of Calls (Best Run)': 22,
                'Genotyping results file id': 'file_id'
            }
            assert self.outputs[self.lims_sample2].udf == {'Number of Calls (This Run)': 22}
            self.lims_sample2.put.assert_called_once()
