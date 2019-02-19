from itertools import cycle

from pyclarity_lims.entities import ReagentLot


from scripts.generate_hamilton_input_ntp import GenerateHamiltonInputNTP
from tests.test_common import TestEPP, FakeEntitiesMaker


class TestGenerateHamiltonInputNTP(TestEPP):
    def setUp(self):

        self.epp = GenerateHamiltonInputNTP(self.default_argv + ['-i', 'a_file_location'] + ['-d', self.assets])

    def test_happy_input(self):
        """
        test that files are written under happy path conditions
        i.e. 1 input plate, 1 output plate, 1 output per input
        """
        fem = FakeEntitiesMaker()
        self.epp.lims = fem.lims
        self.epp.process = fem.create_a_fake_process(
            nb_input=2,
            output_artifact_udf={'NTP Library Volume (uL)': cycle(['50', '40']),
                                 'NTP RSB Volume (uL)': cycle(['10', '20'])}
        )
        self.epp.process.step._reagent_lots.reagent_lots = [
            fem.create_instance(ReagentLot, id='re1', lot_number='LP9999999-RSB'),
            fem.create_instance(ReagentLot, id='re2', lot_number='LP9999999-RSA')
        ]
        self.epp._validate_step()
        self.epp._run()
        expected_lines = [
            'Input Plate,Input Well,Output Plate,Output Well,Library Volume,RSB Barcode,RSB Volume',
            'input_uri_container_1,A1,output_uri_container_2,A1,50,LP9999999-RSB,10',
            'input_uri_container_1,B1,output_uri_container_2,B1,40,LP9999999-RSB,20'
        ]
        assert self.file_content('a_file_location-hamilton_input.csv') == expected_lines
        assert self.stripped_md5('a_file_location-hamilton_input.csv') == 'ba085c7e32740bf8f276f352d280fb37'
        assert self.stripped_md5(self.epp.shared_drive_file_path) == 'ba085c7e32740bf8f276f352d280fb37'
