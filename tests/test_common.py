from os.path import join, dirname, abspath
from unittest.case import TestCase
from EPPs.common import EPP
from unittest.mock import Mock


def fake_all_inputs(unique=False, resolve=False):
    return (
        Mock(samples=[Mock(artifact='artifact_for_sample_1', id='1'), Mock(artifact='artifact_for_sample_2', id='2')]),
        Mock(samples=[Mock(artifact='artifact_for_sample_2', id='3'), Mock(artifact='artifact_for_sample_3', id='4')])
    )


class FakeEntity(Mock):
    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name


class TestCommon(TestCase):
    assets = join(dirname(abspath(__file__)), 'assets')
    genotype_csv = join(assets, 'E03159_WGS_32_panel_9504430.csv')
    genotype_quantStudio = join(assets, 'VGA55_QuantStudio 12K Flex_export.txt')
    small_reference_fai = join(assets, 'genotype_32_SNPs_genome_600bp.fa.fai')
    reference_fai = join(assets, 'GRCh37.fa.fai')
    log_file = join(assets, 'test_log_file.txt')


class TestEPP(TestCommon):
    def setUp(self):
        self.epp = EPP(
            'http://server:8080/some/extra/stuff',
            'a username',
            'a password',
            self.log_file
        )
        self.epp._process = Mock()
        self.epp._lims = Mock()

    def test_init(self):
        assert self.epp.baseuri == 'http://server:8080'