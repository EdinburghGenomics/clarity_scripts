from os.path import join, dirname, abspath
from unittest.case import TestCase

from EPPs.common import StepEPP
from unittest.mock import Mock, PropertyMock, patch


def fake_artifact(id):
    return Mock(
        id='%s'%id,
        workflow_stages_and_statuses=[(Mock(uri='a_uri'), 'COMPLETE', 'stage1')]
    )

def fake_all_inputs(unique=False, resolve=False):
    '''Return a list of mocked artifacts which contain sample which contain artifact ... Simple!'''
    return (
        Mock(samples=[Mock(artifact=fake_artifact(id='a1'), id='s1')]),
        Mock(samples=[Mock(artifact=fake_artifact(id='a2'), id='s2')])
    )

class FakeEntity(Mock):
    def __init__(self, name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name


class TestCommon(TestCase):
    assets = join(dirname(abspath(__file__)), 'assets')
    genotype_csv = join(assets, 'E03159_WGS_32_panel_9504430.csv')
    genotype_quantStudio = join(assets, 'VGA55_QuantStudio 12K Flex_export.txt')
    accufill_log = join(assets, 'OpenArrayLoad_Log.csv')
    small_reference_fai = join(assets, 'genotype_32_SNPs_genome_600bp.fa.fai')
    reference_fai = join(assets, 'GRCh37.fa.fai')
    log_file = join(assets, 'test_log_file.txt')


class TestEPP(TestCommon):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.patched_lims = patch.object(StepEPP, 'lims', new_callable=PropertyMock())
        self.patched_process = patch.object(StepEPP, 'process', new_callable=PropertyMock())

    def setUp(self):
        self.epp = StepEPP(
            'http://server:8080/some/extra/stuff',
            'a username',
            'a password',
            self.log_file
        )

    def test_init(self):
        assert self.epp.baseuri == 'http://server:8080'
