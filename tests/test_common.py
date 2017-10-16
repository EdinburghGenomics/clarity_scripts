from os.path import join, dirname, abspath
from requests import ConnectionError
from unittest.case import TestCase
from unittest.mock import Mock, PropertyMock, patch
import EPPs
from EPPs.common import StepEPP, RestCommunicationEPP, find_newest_artifact_originating_from

class NamedMock(Mock):
    @property
    def name(self):
        return self.real_name


class MockedSamples(NamedMock):
    project = NamedMock(real_name='10015AT')


def fake_artifact(id):
    return Mock(
        id=str(id),
        workflow_stages_and_statuses=[(Mock(uri='a_uri'), 'COMPLETE', 'stage1')]
    )


def fake_all_inputs(unique=False, resolve=False):
    """Return a list of mocked artifacts which contain samples which contain artifacts ... Simple!"""
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
    etc_path = join(abspath(dirname(EPPs.__file__)), 'etc')
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
        self.patched_process = patch.object(StepEPP, 'process', new_callable=PropertyMock(return_value=Mock(id='a_process_id')))

    def setUp(self):
        self.epp = StepEPP('http://server:8080/some/extra/stuff', 'a username', 'a password', self.log_file)

    def test_init(self):
        assert self.epp.baseuri == 'http://server:8080'


class TestRestCommunicationEPP(TestCase):
    @staticmethod
    def fake_rest_interaction(*args, **kwargs):
        if kwargs.get('dodgy'):
            raise ConnectionError('Something broke!')
        return args, kwargs

    def test_interaction(self):
        epp = RestCommunicationEPP()
        assert epp._rest_interaction(self.fake_rest_interaction, 'this', 'that', other='another') == (
            ('this', 'that'), {'other': 'another'}
        )

        with patch('sys.exit') as mocked_exit, patch('builtins.print') as mocked_print:
            epp._rest_interaction(self.fake_rest_interaction, 'this', 'that', dodgy=True)

        mocked_exit.assert_called_with(127)
        mocked_print.assert_called_with('ConnectionError: Something broke!')


class TestFindNewestArtifactOriginatingFrom(TestCase):
    def test_find_newest_artifact_originating_from(self):
        lims = Mock(get_artifacts=Mock(return_value=[
            Mock(id='fx1', parent_process=Mock(id='121')),
            Mock(id='fx2', parent_process=Mock(id='123'))
        ]))
        process_type = 'Process 1.0'
        sample_name = 's1'
        artifact = find_newest_artifact_originating_from(lims, process_type, sample_name)
        assert artifact.id == 'fx2'
        lims.get_artifacts.assert_called_with(type='Analyte', process_type='Process 1.0', sample_name='s1')

        lims = Mock(get_artifacts=Mock(return_value=[
            Mock(id='fx1', parent_process=Mock(id='121')),
        ]))
        artifact = find_newest_artifact_originating_from(lims, process_type, sample_name)
        assert artifact.id == 'fx1'

        lims = Mock(get_artifacts=Mock(return_value=[]))
        artifact = find_newest_artifact_originating_from(lims, process_type, sample_name)
        assert artifact is None
