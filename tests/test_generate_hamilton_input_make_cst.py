from unittest.mock import Mock, PropertyMock, patch

from scripts.generate_hamilton_input_make_cst import GenerateHamiltonInputMakeCST
from tests.test_common import TestEPP, NamedMock


class TestGenerateHamiltonInputMakeCST(TestEPP):
    def setUp(self):
        fake_outputs_per_input = [
            Mock(id='ao1', location=[NamedMock(real_name='container3'), 'A:1'])]

        fake_input_artifact_list = [Mock(location=[NamedMock(real_name='container1'), 'A:1']),
                                    Mock(location=[NamedMock(real_name='container2'), 'A:1']),
                                    Mock(location=[NamedMock(real_name='container2'), 'B:1'])]

        fake_artifact = Mock(type='Analyte', input_artifact_list=Mock(return_value=fake_input_artifact_list))

        fake_inputs = [fake_artifact]

        step_udfs = {'EPX 1 (uL)': '231', 'EPX 2 (uL)': '33', 'EPX 3 (uL)': '121',
                     'HT1 (uL)': '2.5', 'EPX Master Mix (uL)': '35',
                     'PhiX (uL)': '1', 'Library Volume (uL)': '10', 'NaOH (uL)': '2.5',}

        self.patched_process1 = patch.object(
            GenerateHamiltonInputMakeCST,
            'process',
            new_callable=PropertyMock(return_value=Mock(all_inputs=Mock(return_value=fake_inputs),
                                                        udf=step_udfs,
                                                        outputs_per_input=Mock(return_value=fake_outputs_per_input))
                                      ))

        # argument -d left blank to write file to local directory
        self.epp = GenerateHamiltonInputMakeCST(self.default_argv + ['-i', 'a_file_location'] + ['-d', ''])

    def test_generate_hamilton_input_make_cst(self):
        with self.patched_process1:

            self.epp._run()

            expected_file = ['Input Container,Input Well,Output Container,Output Well,EPX 1,EPX 2,EPX 3,HT1,'
                             'EPX Master Mix,PhiX,NaOH,Library',
                            'container1,A1,container3,A1,231,33,121,2.5,35,1,2.5,10',
                             'container2,A1,container3,A1,231,33,121,2.5,35,1,2.5,10',
                             'container2,B1,container3,A1,231,33,121,2.5,35,1,2.5,10']

            expected_md5s = "b72b2c3e9d6df1e8abeabccf31f91ded"

            actual_file = self.file_content('a_file_location-hamilton_input.csv')
            actual_lims_md5s = self.stripped_md5('a_file_location-hamilton_input.csv')
            actual_shared_drive_md5s = self.stripped_md5(self.epp.shared_drive_file_path)

            assert actual_file == expected_file
            assert actual_shared_drive_md5s == expected_md5s
            assert actual_lims_md5s == expected_md5s
