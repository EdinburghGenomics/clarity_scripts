import pytest
from os.path import join
from tests.test_common import TestCommon, TestEPP, FakeEntity
from unittest.mock import Mock, patch
from bin.convert_and_dispatch_genotypes import GenotypeConversion, UploadVcfToSamples


class TestGenotypeConversion(TestCommon):
    test_records = {
        'id1': {'test_sample': '0/1', 'SNP': ['chr2', '120', 'id1', 'T', 'C', '.', '.', '.', 'GT']},
        'id2': {'test_sample': '1/1', 'SNP': ['chr1', '601', 'id2', 'C', 'A', '.', '.', '.', 'GT']},
        'id3': {'test_sample': '1/1', 'SNP': ['chr2', '72', 'id3', 'C', 'T', '.', '.', '.', 'GT']},
        'id4': {'test_sample': '0/1', 'SNP': ['chr1', '200', 'id4', 'A', 'G', '.', '.', '.', 'GT']},
    }

    def setUp(self):
        with open(self.genotype_csv) as open_csv:
            self.geno_conversion = GenotypeConversion(
                open_csv,
                'igmm',
                self.small_reference_fai,
                flank_length=600
            )

    def test_generate_vcf(self):
        # header_lines = ['##header line1', '##header line2']
        # snp_ids = ['id4', 'id2', 'id3', 'id1']
        # TODO: make assertions on what header lines, snp IDs, etc. have been written
        sample_id = '9504430'
        path = join(self.assets, 'test_generate')
        vcf_file = path + '.vcf'
        assert self.geno_conversion.generate_vcf(sample_id, new_name=path) == vcf_file
        with open(vcf_file) as f:
            assert len([l for l in f.readlines() if not l.startswith('#')]) == 32

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
        refence_length = self.geno_conversion.parse_genome_fai(self.small_reference_fai)
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

    def test_init_genotype_csv(self):
        assert self.geno_conversion.sample_names == {'9504430'}
        assert len(self.geno_conversion.all_records) == 32

    def test_init_quantstudio_flex_genotype(self):
        with open(self.genotype_quantStudio) as open_file:
            geno_conversion = GenotypeConversion(open_file, 'quantStudio', self.small_reference_fai, flank_length=600)
            assert geno_conversion.sample_names == {'V0001P001C01', 'V0001P001A01'}
            assert len(geno_conversion.all_records) == 32

    def test_find_field(self):
        observed_fieldnames = ('__this__', 'that', 'OTHER')
        valid_this_fieldnames = ('this', 'THIS', '__this__')
        valid_that_fieldnames = ('that', 'THAT', '__that__')
        valid_other_fieldnames = ('other', 'OTHER', '__other__')

        find = self.geno_conversion._find_field
        assert find(valid_this_fieldnames, observed_fieldnames) == '__this__'
        assert find(valid_that_fieldnames, observed_fieldnames) == 'that'
        assert find(valid_other_fieldnames, observed_fieldnames) == 'OTHER'


fake_all_inputs = Mock(
    return_value=[
        Mock(samples=[FakeEntity(name='this', udf={'User Sample Name': '9504430'}, put=Mock())])
    ]
)


class TestUploadVcfToSamples(TestEPP):
    def setUp(self):
        self.epp = UploadVcfToSamples(
            'http://server:8080/a_step_uri',
            'a_user',
            'a_password',
            self.log_file,
            'igmm',
            file=self.genotype_csv
        )
        self.epp._lims = Mock()
        self.epp._process = Mock(all_inputs=fake_all_inputs)

    def test_upload(self):
        patched_log = patch('bin.convert_and_dispatch_genotypes.UploadVcfToSamples.info')
        patched_generate_vcf = patch('bin.convert_and_dispatch_genotypes.GenotypeConversion.generate_vcf')
        patched_remove = patch('bin.convert_and_dispatch_genotypes.remove')

        exp_log_msgs = (
            ('Matching against %s artifacts', 1),
            ('Matching %s against user sample name %s', 'this', '9504430'),
            ('Matched and uploaded %s artifacts against %s genotype results', 1, 1),
            ('%s artifacts did not match', 0),
            ('%s genotyping results were not used', 0)
        )

        with patched_log as p, patched_generate_vcf, patched_remove:
            self.epp._run()
            for m in exp_log_msgs:
                p.assert_any_call(*m)
