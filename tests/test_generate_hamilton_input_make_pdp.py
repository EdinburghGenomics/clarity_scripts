from unittest.mock import PropertyMock, Mock, patch

from scripts.generate_hamilton_input_make_pdp import GenerateHamiltonInputMakePDP
from tests.test_common import TestEPP, NamedMock


class TestGenerateHamiltonInputPDP(TestEPP):

    def setUp(self):
        fake_outputs_per_input = [
            Mock(id='ao1', location=[NamedMock(real_name='container3'), 'A:1'])]

        fake_input_artifact_list = [Mock(location=[NamedMock(real_name='container1'), 'A:1']),
                                    Mock(location=[NamedMock(real_name='container2'), 'A:1']),
                                    Mock(location=[NamedMock(real_name='container2'), 'B:1'])]

        fake_artifact = Mock(type='Analyte',udf={'NTP Volume (uL)':5}, input_artifact_list=Mock(return_value=fake_input_artifact_list))

        fake_inputs = [fake_artifact]

        self.patched_process1 = patch.object(
            GenerateHamiltonInputMakePDP,
            'process',
            new_callable=PropertyMock(return_value=Mock(all_inputs=Mock(return_value=fake_inputs),
                                                        outputs_per_input=Mock(return_value=fake_outputs_per_input))
                                      ))

        # argument -d left blank to write file to local directory
        self.epp = GenerateHamiltonInputMakePDP(self.default_argv + ['-i', 'a_file_location'] + ['-d', ''])

    def test_run(self):  # test that file is written under happy path conditions i.e. <=9 input plates, 1 output
        with self.patched_process1:
            self.epp._run()
            expected_file = [
                'Input Plate,Input Well,Output Plate,Output Well,Library Volume',
                'container1,A1,container3,A1,5',
                'container2,A1,container3,A1,5',
                'container2,B1,container3,A1,5'
            ]
            expected_md5 = 'd24f396c94712a544166d29b283d49c2'

            assert self.file_content('a_file_location-hamilton_input.csv') == expected_file
            assert self.stripped_md5('a_file_location-hamilton_input.csv') == expected_md5
            assert self.stripped_md5(self.epp.shared_drive_file_path) == expected_md5
