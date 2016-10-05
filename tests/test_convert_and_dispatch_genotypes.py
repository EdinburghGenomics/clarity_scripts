import os
from sys import version_info
from unittest.case import TestCase
from EPPs.convert_and_dispatch_genotypes import GenotypeConversion

if version_info.major == 2:
    from mock import patch
    import __builtin__ as builtins
else:
    import builtins
    from unittest.mock import patch


class TestGenotypeConversion(TestCase):
    def setUp(self):
        self.genotype_csv = os.path.join(os.path.dirname(__file__), 'test_data', 'E03159_WGS_32_panel_9504430.csv')
        self.genotype_quantStudio = os.path.join(os.path.dirname(__file__), 'test_data', 'VGA55_QuantStudio 12K Flex_export.txt')
        self.small_reference_fai = os.path.join(os.path.dirname(__file__), 'test_data', 'genotype_32_SNPs_genome_600bp.fa.fai')
        self.reference_fai = os.path.join(os.path.dirname(__file__), 'test_data', 'GRCh37.fa.fai')
        self.test_records = {
            'id1': {'test_sample': '0/1', 'SNP': ['chr2', '120', 'id1', 'T', 'C', '.', '.', '.', 'GT']},
            'id2': {'test_sample': '1/1', 'SNP': ['chr1', '601', 'id2', 'C', 'A', '.', '.', '.', 'GT']},
            'id3': {'test_sample': '1/1', 'SNP': ['chr2', '72', 'id3', 'C', 'T', '.', '.', '.', 'GT']},
            'id4': {'test_sample': '0/1', 'SNP': ['chr1', '200', 'id4', 'A', 'G', '.', '.', '.', 'GT']},
        }
        with open(self.genotype_csv) as open_csv:
            self.geno_conversion = GenotypeConversion(
                open_csv,
                self.small_reference_fai,
                'igmm',
                flank_length=600
            )

    def test_generate_vcf(self):
        header_lines = ['##header line1', '##header line2']
        snp_ids = ['id4', 'id2', 'id3', 'id1']
        sample_id = '9504430'

        with patch.object(builtins, 'open') as patched_open:
            vcf_file = self.geno_conversion.generate_vcf(sample_id)
            assert vcf_file == sample_id + '.vcf'
            assert patched_open.call_count == 1
            # TODO: check that the write function has been called

    def test_get_genotype_from_call(self):
        genotype = self.geno_conversion.get_genotype_from_call('A', 'T', 'Both', )
        assert genotype == '0/1'
        genotype = self.geno_conversion.get_genotype_from_call('A', 'T', 'Undefined')
        assert genotype == './.'
        self.assertRaises(ValueError, self.geno_conversion.get_genotype_from_call, 'G', 'T', 'A')

    def test_vcf_header_from_fai_file(self):
        expected_vcf_headers = [
            '##contig=<ID=test1,length=48>', '##contig=<ID=test2,length=656>',
            '##contig=<ID=test3,length=35>', '##contig=<ID=test4,length=10>'
        ]
        reference_length=[('test1', '48'), ('test2', '656'), ('test3', '35'), ('test4', '10')]
        tested_vcf_header = self.geno_conversion.vcf_header_from_ref_length(reference_length)
        assert expected_vcf_headers == tested_vcf_header

    def test_order_from_fai(self):
        reference_length = [
            ('chr1', '2000'),
            ('chr2', '2000'),
        ]
        expected_records = ['id4', 'id2', 'id3', 'id1']
        assert self.geno_conversion.order_from_fai(self.test_records, reference_length) == expected_records

    def test_parse_genome_fai(self):
        refence_length = self.geno_conversion.parse_genome_fai(self.small_reference_fai)
        expected_ref_length = [
            ('C___2728408_10', '1201'), ('C___1563023_10', '1201'), ('C__15935210_10', '1201'),
            ('C__33211212_10', '1201'), ('C___3227711_10', '1201'), ('C__30044763_10', '1201'),
            ('C__11821218_10', '1201'), ('C___1670459_10', '1201'), ('C__29619553_10', '1201'),
            ('C___1007630_10', '1201'), ('C__26546714_10', '1201'), ('C___7421900_10', '1201'),
            ('C__27402849_10', '1201'), ('C___2953330_10', '1201'), ('C__16205730_10', '1201'),
            ('C___8850710_10', '1201'), ('C___1801627_20', '1201'), ('C___7431888_10', '1201'),
            ('C___1250735_20', '1201'), ('C___1902433_10', '1201'), ('C__31386842_10', '1201'),
            ('C__26524789_10', '1201'), ('C___8924366_10', '1201'), ('C_____43852_10', '1201'),
            ('C__11522992_10', '1201'), ('C__10076371_10', '1201'), ('C___7457509_10', '1201'),
            ('C___1122315_10', '1201'), ('C__11710129_10', '1201'), ('C___1027548_20', '1201'),
            ('C___8938211_20', '1201'), ('C___1083232_10', '1201')
        ]

        assert refence_length == expected_ref_length

    def test_parse_genotype_csv(self):
        with open(self.genotype_csv) as open_csv:
            # all_records, all_samples = self.geno_conversion.parse_genotype_csv()
            assert self.geno_conversion.sample_names == {'9504430'}
            assert len(self.geno_conversion.all_records) == 32

    def test_parse_quantstudio_aif_genotype(self):
        pass
        with open(self.genotype_quantStudio) as open_file:
            geno_conversion = GenotypeConversion(open_file, self.small_reference_fai, 'quantStudio', flank_length=600)
            assert geno_conversion.sample_names == {'V0001P001C01', 'V0001P001A01'}
            assert len(geno_conversion.all_records) == 32
