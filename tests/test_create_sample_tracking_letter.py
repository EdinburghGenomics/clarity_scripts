from os.path import join, dirname, abspath
from unittest.mock import PropertyMock, Mock

from EPPs.common import StepEPP
from scripts.create_sample_tracking_letter import GenerateTrackingLetter
from tests.test_common import TestEPP, NamedMock, patch


class TestCreateTrackingLetter(TestEPP):
    sample1 = Mock(project=NamedMock(real_name='project1'))
    artifact1 = Mock(container=NamedMock(real_name='container1'), samples=[sample1])
    artifact2 = Mock(container=NamedMock(real_name='container2'))

    patched_process1 = patch.object(
        StepEPP,
        'process',
        new_callable=PropertyMock(return_value=Mock(
            all_inputs=Mock(return_value=[artifact1]))))

    patched_process2 = patch.object(
        StepEPP,
        'process',
        new_callable=PropertyMock(return_value=Mock(
            all_inputs=Mock(return_value=[artifact1, artifact2]))))

    def setUp(self):
        super().setUp()
        self.epp = GenerateTrackingLetter(self.default_argv + [
            '--letter', join(dirname(abspath(__file__)), 'assets', '99-99999')]
                                          )

    def test_generate_letter_happy_path(self):
        with self.patched_process1, self.patched_lims, patch('docx.document.Document.save') as mocked_save:
            self.epp._run()

            mocked_save.assert_called_with(join(dirname(abspath(__file__)),'assets','99-99999-Edinburgh_Genomics_Sample_Tracking_Letter_project1.docx'))