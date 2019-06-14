from unittest.mock import PropertyMock, Mock, patch

from scripts.generate_hamilton_input_make_pdp_mix import GenerateHamiltonInputMakePDPMix
from tests.test_common import TestEPP, NamedMock


class TestGenerateHamiltonInputPDP(TestEPP):

    def setUp(self):
        fake_outputs_per_input = [
            Mock(id='ao1', location=[NamedMock(real_name='container3'), 'A:1'])]

        fake_input_artifact_list = [Mock(location=[NamedMock(real_name='container1'), 'A:1']),
                                    Mock(location=[NamedMock(real_name='container2'), 'A:1']),
                                    Mock(location=[NamedMock(real_name='container2'), 'B:1'])]

        fake_artifact = Mock(type='Analyte',udf={'NTP Volume (uL)':7}, input_artifact_list=Mock(return_value=fake_input_artifact_list))
        fake_artifact2 = Mock(type='Analyte', udf={'NTP Volume (uL)': 25},
                             input_artifact_list=Mock(return_value=fake_input_artifact_list))

        fake_inputs = [fake_artifact]
        fake_inputs2 = [fake_artifact2]

        self.patched_process1 = patch.object(
            GenerateHamiltonInputMakePDPMix,
            'process',
            new_callable=PropertyMock(return_value=Mock(all_inputs=Mock(return_value=fake_inputs),
                                                        outputs_per_input=Mock(return_value=fake_outputs_per_input))
                                      ))
        self.patched_process2 = patch.object(
            GenerateHamiltonInputMakePDPMix,
            'process',
            new_callable=PropertyMock(return_value=Mock(all_inputs=Mock(return_value=fake_inputs2),
                                                        outputs_per_input=Mock(return_value=fake_outputs_per_input))
                                      ))

        # argument -d left blank to write file to local directory
        self.epp = GenerateHamiltonInputMakePDPMix(self.default_argv + ['-i', 'a_file_location'] + ['-d', ''])

    def test_run(self):  # test that file is written under happy path conditions i.e. 1 input plate, 1 output
        with self.patched_process1:
            self.epp._run()
            expected_file = [
                'Output Plate,Output Well,Mix Volume',
                'container3,A1,16',
            ]
            expected_md5 = '0fd0e782bacb5887906028d85b1d216d'

            actual_file = self.file_content('a_file_location-hamilton_input.csv')
            actual_md5_lims = self.stripped_md5('a_file_location-hamilton_input.csv')
            actual_md5_shared_drive = self.stripped_md5(self.epp.shared_drive_file_path)

            assert actual_file == expected_file
            assert actual_md5_lims == expected_md5
            assert actual_md5_shared_drive == expected_md5

    def test_high_mix_volume(self):  # test that maximum mix volume is 50 ul even if sum of the NTP volume is greater
        with self.patched_process2:
            self.epp._run()
            expected_file = [
                'Output Plate,Output Well,Mix Volume',
                'container3,A1,50',
            ]
            expected_md5 = '3ea758f77a402fa587417c60ae311d66'

            actual_file = self.file_content('a_file_location-hamilton_input.csv')
            actual_md5_lims = self.stripped_md5('a_file_location-hamilton_input.csv')
            actual_md5_shared_drive = self.stripped_md5(self.epp.shared_drive_file_path)

            assert actual_file == expected_file
            assert actual_md5_lims == expected_md5
            assert actual_md5_shared_drive == expected_md5
