import sys
from os.path import join, dirname, abspath
from unittest.case import TestCase
from EPPs.common import EPP

if sys.version_info.major == 2:
    from mock import patch
    import __builtin__ as builtins
else:
    import builtins
    from unittest.mock import patch


class TestCommon(TestCase):
    assets = join(dirname(abspath(__file__)), 'assets')
    genotype_csv = join(assets, 'E03159_WGS_32_panel_9504430.csv')
    genotype_quantStudio = join(assets, 'VGA55_QuantStudio 12K Flex_export.txt')
    small_reference_fai = join(assets, 'genotype_32_SNPs_genome_600bp.fa.fai')
    reference_fai = join(assets, 'GRCh37.fa.fai')


class TestEPP(TestCommon):
    def setUp(self):
        self.epp = EPP(
            'http://server:8080/some/extra/stuff',
            'a username',
            'a password',
            join(self.assets, 'test_log_file.txt')
        )

    def test_init(self):
        assert self.epp.baseuri == 'http://server:8080'
