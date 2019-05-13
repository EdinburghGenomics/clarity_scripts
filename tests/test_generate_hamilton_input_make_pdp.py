from scripts.generate_hamilton_input_make_pdp import GenerateHamiltonInputMakePDP
from tests.test_common import TestEPP, FakeEntitiesMaker


class TestGenerateHamiltonInputCFP(TestEPP):
    def setUp(self):
        # argument -d left blank to write file to local directory
        self.epp = GenerateHamiltonInputMakePDP(self.default_argv + ['-i', 'a_file_location'] + ['-d', ''])

    def test_run(self):  # test that file is written under happy path conditions i.e. <=9 input plates, 1 output
        fem = FakeEntitiesMaker()
        self.epp.lims = fem.lims
        self.epp.process = fem.create_a_fake_process(
            nb_input=2,
            step_udfs={'Library Volume (uL)': '5'}
        )

        self.epp._run()
        expected_file = [
            'Input Plate,Input Well,Output Plate,Output Well,Library Volume',
            'input_uri_container_1,A1,output_uri_container_2,A1,5',
            'input_uri_container_1,B1,output_uri_container_2,B1,5'
        ]
        expected_md5 = 'f144811c3d200f184670c2befe4e9ee7'

        assert self.file_content('a_file_location-hamilton_input.csv') == expected_file
        assert self.stripped_md5('a_file_location-hamilton_input.csv') == expected_md5
        assert self.stripped_md5(self.epp.shared_drive_file_path) == expected_md5
