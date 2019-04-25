from itertools import cycle

from pyclarity_lims.entities import ReagentLot

from scripts.generate_hamilton_input_qpcr_dilution import GenerateHamiltonInputQPCRDilution
from tests.test_common import TestEPP, FakeEntitiesMaker

class TestGenerateHamiltonInputQPCRDilution(TestEPP):

    def setUp(self):
        # argument -d left blank to write file to local directory
        self.epp = GenerateHamiltonInputQPCRDilution(self.default_argv + ['-i', 'a_file_location'] + ['-d', ''])

    def test_generate_hamilton_input_qpcr_dilution(self):

        fem= FakeEntitiesMaker()
        self.epp.lims=fem.lims
        self.epp.process = fem.create_a_fake_process(
            nb_input=3,
            output_artifact_udf={'RSB Volume (ul)': cycle(['10','9','8'])},
            step_udfs={'DCT Volume (ul)': '15'},
            output_type='ResultFile'

        )
        self.epp.process.step._reagent_lots.reagent_lots = [
            fem.create_instance(ReagentLot, id='re1', lot_number='LP9999999-RSB')
        ]
        self.epp._validate_step()

        self.epp._run()

        expected_file_contents = ['Input Plate,Input Well,Output Plate,Output Well,Sample Volume,Buffer Barcode,Buffer Volume',
                                    'input_uri_container_1,A1,output_uri_container_2,A1,15,LP9999999-RSB,10',
                                    'input_uri_container_1,B1,output_uri_container_2,B1,15,LP9999999-RSB,9',
                                    'input_uri_container_1,C1,output_uri_container_2,C1,15,LP9999999-RSB,8']
        expected_file_md5sums = '9a8deafa1861beb5899cbbe3f352d00b'

        actual_file_lims_contents = self.file_content('a_file_location-hamilton_input.csv')
        actual_file_shareddrive_contents = self.file_content(self.epp.shared_drive_file_path)
        actual_file_lims_md5sums = self.stripped_md5('a_file_location-hamilton_input.csv')
        actual_file_shareddrive_md5sums = self.stripped_md5(self.epp.shared_drive_file_path)


        assert expected_file_contents == actual_file_lims_contents
        assert expected_file_contents == actual_file_shareddrive_contents
        assert actual_file_lims_md5sums == expected_file_md5sums
        assert actual_file_shareddrive_md5sums ==  expected_file_md5sums