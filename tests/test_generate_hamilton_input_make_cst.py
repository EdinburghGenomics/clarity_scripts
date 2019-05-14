from scripts.generate_hamilton_input_make_cst import GenerateHamiltonInputMakeCST
from tests.test_common import TestEPP, FakeEntitiesMaker


class TestGenerateHamiltonInputMakeCST(TestEPP):
    def setUp(self):
        self.epp = GenerateHamiltonInputMakeCST(self.default_argv + ['-i', 'a_file_location'] + ['-d', ''])
        self.fem = FakeEntitiesMaker()

    def test_generate_hamilton_input_make_cst(self):
        self.epp.lims = self.fem.lims
        self.epp.process = self.fem.create_a_fake_process(step_udfs)
        self.epp._run()

        expected_file = ""
        expected_md5s = ""

        actual_file = self.file_content('a_file_location-hamilton_input.csv')
        actual_lims_md5s = self.stripped_md5('a_file_location-hamilton_input.csv')
        actual_shared_drive_md5s = self.stripped_md5(self.epp.shared_drive_file_path)

        print(self.file_content('a_file_location-hamilton_input.csv'))
        print(self.stripped_md5('a_file_location-hamilton_input.csv'))

        #assert actual_file == expected_file
        #assert actual_shared_drive_md5s == expected_md5s
        #assert actual_lims_md5s == expected_md5s
