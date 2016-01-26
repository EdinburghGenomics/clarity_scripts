import os
from unittest.case import TestCase
from EPPs.convert_and_dispatch_genotypes import convert_genotype_csv, get_genotype_from_call, vcf_header_from_fai_file, \
    order_from_fai

__author__ = 'tcezard'


class Test_small_tools(TestCase):
    def setUp(self):
        self.genotype_csv = os.path.join(os.path.dirname(__file__), 'test_data','E03159_WGS_32_panel_9504430.csv')
        self.genotype_csv = os.path.join(os.path.dirname(__file__), 'test_data','E03159_WGS_32_panel.csv')
        self.small_reference_fai = os.path.join(os.path.dirname(__file__), 'test_data','genotype_32_SNPs_genome_600bp.fa.fai')
        self.reference_fai = os.path.join(os.path.dirname(__file__), 'test_data','GRCh37.fa.fai')

    def test_convert_genotype_csv(self):
        vcf_text = """#CHROM	POS	ID	REF	ALT	QUAL	FILTER	INFO	FORMAT	50293
1	163289571	rs2136241	C	T	.	.	GT	1/1
1	208068579	rs2259397	T	A	.	.	GT	1/1
1	59569829	rs3010325	C	T	.	.	GT	0/1
10	117923225	rs4751955	A	.	.	.	GT	./.
10	1511786	rs1533486	T	G	.	.	GT	0/1
12	23769449	rs10771010	T	C	.	.	GT	1/1
12	28781965	rs12318959	C	.	.	.	GT	./.
13	43173198	rs3742257	T	.	.	.	GT	0/0
14	25843774	rs1377935	T	.	.	.	GT	0/0
14	55932919	rs946065	C	.	.	.	GT	./.
15	99130113	rs6598531	T	.	.	.	GT	0/0
16	82622140	rs4783229	T	C	.	.	GT	0/1
18	35839365	rs1567612	G	A	.	.	GT	0/1
18	42481985	rs11660213	A	G	.	.	GT	0/1
19	39697974	rs11083515	A	G	.	.	GT	1/1
2	11200347	rs7564899	G	A	.	.	GT	0/1
2	21084332	rs4971536	C	.	.	.	GT	0/0
2	50525067	rs10194978	G	A	.	.	GT	0/1
3	181638250	rs4855056	A	G	.	.	GT	0/1
5	11870138	rs6554653	C	T	.	.	GT	1/1
6	125039942	rs1415762	C	.	.	.	GT	0/0
6	163719115	rs6927758	C	.	.	.	GT	./.
6	25548288	rs441460	G	A	.	.	GT	1/1
6	37572144	rs7773994	T	.	.	.	GT	0/0
6	9914294	rs9396715	T	.	.	.	GT	0/0
7	126113335	rs7796391	A	G	.	.	GT	1/1
8	1033625	rs2336695	A	G	.	.	GT	1/1
8	104215466	rs1157213	T	C	.	.	GT	0/1
9	80293657	rs10869955	C	A	.	.	GT	0/1
Y	14850341	rs2032598	T	.	.	.	GT	./.
Y	6818291	rs768983	C	.	.	.	GT	./.
Y	8602518	rs3913290	C	.	.	.	GT	./."""
        #text=convert_genotype_csv(self.genotype_csv,self.reference_fai)
        #print(text)
        #self.assertEqual(text,vcf_text)

        text=convert_genotype_csv(self.genotype_csv, self.small_reference_fai, 600)

        #print(text)


    def test_get_genotype_from_call(self):
        genotype = get_genotype_from_call('A', 'T', 'Both', )
        assert genotype == '0/1'
        genotype = get_genotype_from_call('A', 'T', 'Undefined')
        assert genotype == './.'
        self.assertRaises(ValueError, get_genotype_from_call, 'G', 'T', 'A')


    def test_vcf_header_from_fai_file(self):
        vcf_headers = ['##contig=<ID=C___2728408_10,length=1201>', '##contig=<ID=C___1563023_10,length=1201>',
                       '##contig=<ID=C__15935210_10,length=1201>', '##contig=<ID=C__33211212_10,length=1201>',
                       '##contig=<ID=C___3227711_10,length=1201>', '##contig=<ID=C__30044763_10,length=1201>',
                       '##contig=<ID=C__11821218_10,length=1201>', '##contig=<ID=C___1670459_10,length=1201>',
                       '##contig=<ID=C__29619553_10,length=1201>', '##contig=<ID=C___1007630_10,length=1201>',
                       '##contig=<ID=C__26546714_10,length=1201>', '##contig=<ID=C___7421900_10,length=1201>',
                       '##contig=<ID=C__27402849_10,length=1201>', '##contig=<ID=C___2953330_10,length=1201>',
                       '##contig=<ID=C__16205730_10,length=1201>', '##contig=<ID=C___8850710_10,length=1201>',
                       '##contig=<ID=C___1801627_20,length=1201>', '##contig=<ID=C___7431888_10,length=1201>',
                       '##contig=<ID=C___1250735_20,length=1201>', '##contig=<ID=C___1902433_10,length=1201>',
                       '##contig=<ID=C__31386842_10,length=1201>', '##contig=<ID=C__26524789_10,length=1201>',
                       '##contig=<ID=C___8924366_10,length=1201>', '##contig=<ID=C_____43852_10,length=1201>',
                       '##contig=<ID=C__11522992_10,length=1201>', '##contig=<ID=C__10076371_10,length=1201>',
                       '##contig=<ID=C___7457509_10,length=1201>', '##contig=<ID=C___1122315_10,length=1201>',
                       '##contig=<ID=C__11710129_10,length=1201>', '##contig=<ID=C___1027548_20,length=1201>',
                       '##contig=<ID=C___8938211_20,length=1201>', '##contig=<ID=C___1083232_10,length=1201>']
        tested_vcf_header = vcf_header_from_fai_file(self.small_reference_fai)
        assert vcf_headers == tested_vcf_header

    def test_order_from_fai(self):
        records = {
                      'C___2728408_10':[
                          ('C___2728408_10', '60'),
                          ('C___2728408_10', '93'),
                          ('C___2728408_10', '76'),
                          ('C___2728408_10', '2')
                      ],
                      'C__33211212_10':[
                          ('C__33211212_10', '60'),
                          ('C__33211212_10', '43'),
                          ('C__33211212_10', '76'),
                          ('C__33211212_10', '21')
                      ]
        }
        expected_records = ['C___2728408_10\t2', 'C___2728408_10\t60', 'C___2728408_10\t76', 'C___2728408_10\t93',
                            'C__33211212_10\t21', 'C__33211212_10\t43', 'C__33211212_10\t60', 'C__33211212_10\t76']
        assert order_from_fai(records, self.small_reference_fai) == expected_records