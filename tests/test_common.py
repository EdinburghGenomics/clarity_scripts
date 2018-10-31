import hashlib
import os
from os.path import join, dirname, abspath
from requests import ConnectionError
from unittest.case import TestCase
from unittest.mock import Mock, PropertyMock, patch
import EPPs
from EPPs.common import StepEPP, RestCommunicationEPP, find_newest_artifact_originating_from


class NamedMock(Mock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        real_name = kwargs.get('real_name')
        if real_name:
            self.name = real_name


def fake_artifact(_id):
    return Mock(
        id=str(_id),
        workflow_stages_and_statuses=[(Mock(uri='a_uri'), 'COMPLETE', 'stage1')]
    )


def fake_all_inputs(unique=False, resolve=False):
    """Return a list of mocked artifacts which contain samples which contain artifacts... Simple!"""
    return (
        Mock(samples=[Mock(artifact=fake_artifact('a1'), id='s1')]),
        Mock(samples=[Mock(artifact=fake_artifact('a2'), id='s2')])
    )


class TestCommon(TestCase):
    assets = join(dirname(abspath(__file__)), 'assets')
    etc_path = join(abspath(dirname(EPPs.__file__)), 'etc')
    genotype_quantstudio = join(assets, 'YOA15_QuantStudio 12K Flex_export.txt')
    log_file = join(assets, 'test_log_file.txt')


class TestEPP(TestCommon):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.patched_lims = patch.object(StepEPP, 'lims', new_callable=PropertyMock())
        self.default_argv = [
            '--step_uri', 'http://server:8080/a_step_uri',
            '--username', 'a_user',
            '--password', 'a_password',
            '--log_file', TestCommon.log_file
        ]
        os.environ['CLARITYSCRIPTCONFIG'] = join(self.etc_path, 'example_clarity_script.yml')

    def setUp(self):
        argv = self.default_argv.copy()
        argv[1] = 'http://server:8080/some/extra/stuff'
        self.epp = StepEPP(argv)

    def test_init(self):
        assert self.epp.baseuri == 'http://server:8080'

    @staticmethod
    def stripped_md5(fname):
        hash_md5 = hashlib.md5()
        with open(fname, 'rb') as f:
            for line in f:
                hash_md5.update(line.strip())
        return hash_md5.hexdigest()

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
        lims = Mock()
        lims.get_artifacts.return_value = [
            Mock(id='fx1', parent_process=Mock(id='121')),
            Mock(id='fx2', parent_process=Mock(id='123'))
        ]
        process_type = 'Process 1.0'
        sample_name = 's1'
        artifact = find_newest_artifact_originating_from(lims, process_type, sample_name)
        assert artifact.id == 'fx2'
        lims.get_artifacts.assert_called_with(type='Analyte', process_type='Process 1.0', sample_name='s1')

        lims.get_artifacts.return_value = [
            Mock(id='fx1', parent_process=Mock(id='121')),
        ]
        artifact = find_newest_artifact_originating_from(lims, process_type, sample_name)
        assert artifact.id == 'fx1'

        lims.get_artifacts.return_value = []
        artifact = find_newest_artifact_originating_from(lims, process_type, sample_name)
        assert artifact is None