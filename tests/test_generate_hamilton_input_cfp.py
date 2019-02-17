from pyclarity_lims.entities import ReagentLot

from scripts.generate_hamilton_input_cfp import GenerateHamiltonInputCFP
from tests.test_common import TestEPP, NamedMock, FakeEntitiesMaker


class TestGenerateHamiltonInputCFP(TestEPP):
    def setUp(self):
        # argument -d left blank to write file to local directory
        self.epp = GenerateHamiltonInputCFP(self.default_argv + ['-i', 'a_file_location'] + ['-d', ''])

    def test_run(self):  # test that file is written under happy path conditions i.e. <=9 input plates, 1 output
        fem = FakeEntitiesMaker()
        self.epp.lims = fem.lims
        self.epp.process = fem.create_a_fake_process(
            nb_input=2,
            output_artifact_udf={'CFP_DNA_Volume (uL)': '50', 'CFP_RSB_Volume (uL)': '10'}
        )
        self.epp.process.step._reagent_lots.reagent_lots = [
            fem.create_instance(ReagentLot, id='re1', lot_number='LP9999999-RSB'),
            fem.create_instance(ReagentLot, id='re2', lot_number='LP9999999-RSA')
        ]
        self.epp._run()
        expected_file = [
            'Input Plate,Input Well,Output Plate,Output Well,DNA Volume,RSB Barcode,RSB Volume',
            'input_uri_container_1,A1,output_uri_container_2,A1,50,LP9999999-RSB,10',
            'input_uri_container_1,A2,output_uri_container_2,A2,50,LP9999999-RSB,10'
        ]
        assert self.file_content('a_file_location-hamilton_input.csv') == expected_file
        assert self.stripped_md5('a_file_location-hamilton_input.csv') == 'e8e966b3b7a3f38e93d05db04b56266c'
        assert self.stripped_md5(self.epp.shared_drive_file_path) == 'e8e966b3b7a3f38e93d05db04b56266c'
