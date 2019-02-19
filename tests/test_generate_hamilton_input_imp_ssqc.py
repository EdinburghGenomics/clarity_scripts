from itertools import cycle
from pyclarity_lims.entities import ReagentLot

from scripts.generate_hamilton_input_imp_ssqc import GenerateHamiltonInputIMPSSQC
from tests.test_common import TestEPP, FakeEntitiesMaker


class TestGenerateHamiltonInputIMP(TestEPP):
    def setUp(self):
        self.epp = GenerateHamiltonInputIMPSSQC(self.default_argv + ['-i', 'an_imp_file_location'] + ['-d', ''])

    def test_happy_input(self):  # test that file is written under happy path conditions i.e. 1 input plate, 1 output
        fem = FakeEntitiesMaker()
        self.epp.lims = fem.lims
        self.epp.process = fem.create_a_fake_process(
            nb_input=2,
            output_per_input=2,
            nb_output_container=2,
            output_container_name=cycle(['OutputName1-SSQC', 'OutputName2-IMP']),
            step_udfs={
                'CFP to IMP Volume (ul)': '50',
                'CFP to SSQC Volume (ul)': '2',
                'RSB to SSQC Volume (ul)': '8',
            })
        self.epp.process.step._reagent_lots.reagent_lots = [
            fem.create_instance(ReagentLot, id='re1', lot_number='LP9999999-RSB'),
        ]
        self.epp.run()
        expected_file = [
            ','.join(self.epp.csv_column_headers),
            'input_uri_container_1,A1,OutputName2-IMP,A1,50,OutputName1-SSQC,A1,2,LP9999999-RSB,8',
            'input_uri_container_1,B1,OutputName2-IMP,B1,50,OutputName1-SSQC,B1,2,LP9999999-RSB,8'
        ]
        assert self.file_content('an_imp_file_location-hamilton_input.csv') == expected_file
        assert self.stripped_md5('an_imp_file_location-hamilton_input.csv') == 'ab4d89f6c5dd2eed08fd92478a538d9c'
