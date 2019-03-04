import pytest
from pyclarity_lims.entities import ReagentLot

from EPPs.common import InvalidStepError
from scripts.generate_hamilton_input_seq_quant_plate import GenerateHamiltonInputSeqQuantPlate
from tests.test_common import TestEPP, FakeEntitiesMaker


class TestGenerateHamiltonSeqQuantPlate(TestEPP):
    def setUp(self):
        self.epp = GenerateHamiltonInputSeqQuantPlate(
            self.default_argv + ['-i', 'a_file_location'] + ['-d', self.assets])

    def test_happy_input(self):
        """
        test that files are written under happy path conditions
        i.e. up to 9 input plates, 1 output plate, 3 replicates per input
        """
        fem = FakeEntitiesMaker()
        self.epp.lims = fem.lims
        self.epp.process = fem.create_a_fake_process(
            nb_input=9,
            input_name=iter([None, "SDNA Std A1", "SDNA Std B1", "SDNA Std C1", "SDNA Std D1",
                             "SDNA Std E1", "SDNA Std F1", "SDNA Std G1", "SDNA Std H1"]),
            output_per_input=3,
            output_type='ResultFile',
            step_udfs={'Sample Volume (ul)': '2', 'Master Mix Volume (ul)': '198'}
        )

        self.epp.process.step._reagent_lots.reagent_lots = [
            fem.create_instance(ReagentLot, id='re1', lot_number='LP9999999-SDNA'),
        ]
        self.epp._validate_step()
        self.epp._run()
        expected_lines = [
            ','.join(self.epp.csv_column_headers),
            'input_art_A:1_output_1,input_uri_container_1,A1,2,output_uri_container_2,A1,198',
            'input_art_A:1_output_2,input_uri_container_1,A1,2,output_uri_container_2,B1,198',
            'input_art_A:1_output_3,input_uri_container_1,A1,2,output_uri_container_2,C1,198',
            'SDNA Std A1_output_1,LP9999999-SDNA,A1,2,output_uri_container_2,D1,198',
            'SDNA Std A1_output_2,LP9999999-SDNA,A1,2,output_uri_container_2,E1,198',
            'SDNA Std A1_output_3,LP9999999-SDNA,A1,2,output_uri_container_2,F1,198',
            'SDNA Std B1_output_1,LP9999999-SDNA,B1,2,output_uri_container_2,G1,198',
            'SDNA Std B1_output_2,LP9999999-SDNA,B1,2,output_uri_container_2,H1,198',
            'SDNA Std B1_output_3,LP9999999-SDNA,B1,2,output_uri_container_2,A2,198',
            'SDNA Std C1_output_1,LP9999999-SDNA,C1,2,output_uri_container_2,B2,198',
            'SDNA Std C1_output_2,LP9999999-SDNA,C1,2,output_uri_container_2,C2,198',
            'SDNA Std C1_output_3,LP9999999-SDNA,C1,2,output_uri_container_2,D2,198',
            'SDNA Std D1_output_1,LP9999999-SDNA,D1,2,output_uri_container_2,E2,198',
            'SDNA Std D1_output_2,LP9999999-SDNA,D1,2,output_uri_container_2,F2,198',
            'SDNA Std D1_output_3,LP9999999-SDNA,D1,2,output_uri_container_2,G2,198',
            'SDNA Std E1_output_1,LP9999999-SDNA,E1,2,output_uri_container_2,H2,198',
            'SDNA Std E1_output_2,LP9999999-SDNA,E1,2,output_uri_container_2,A3,198',
            'SDNA Std E1_output_3,LP9999999-SDNA,E1,2,output_uri_container_2,B3,198',
            'SDNA Std F1_output_1,LP9999999-SDNA,F1,2,output_uri_container_2,C3,198',
            'SDNA Std F1_output_2,LP9999999-SDNA,F1,2,output_uri_container_2,D3,198',
            'SDNA Std F1_output_3,LP9999999-SDNA,F1,2,output_uri_container_2,E3,198',
            'SDNA Std G1_output_1,LP9999999-SDNA,G1,2,output_uri_container_2,F3,198',
            'SDNA Std G1_output_2,LP9999999-SDNA,G1,2,output_uri_container_2,G3,198',
            'SDNA Std G1_output_3,LP9999999-SDNA,G1,2,output_uri_container_2,H3,198',
            'SDNA Std H1_output_1,LP9999999-SDNA,H1,2,output_uri_container_2,A4,198',
            'SDNA Std H1_output_2,LP9999999-SDNA,H1,2,output_uri_container_2,B4,198',
            'SDNA Std H1_output_3,LP9999999-SDNA,H1,2,output_uri_container_2,C4,198'
        ]

        assert self.file_content('a_file_location-hamilton_input.csv') == expected_lines
        assert self.stripped_md5('a_file_location-hamilton_input.csv') == '178192b55f56493f68c2f37c8bb76cdd'
        assert self.stripped_md5(self.epp.shared_drive_file_path) == '178192b55f56493f68c2f37c8bb76cdd'

    def test_no_reagent(self):  # the function raises an exception if >3 output artifacts for one input
        fem = FakeEntitiesMaker()
        self.epp.lims = fem.lims
        self.epp.process = fem.create_a_fake_process(
            nb_input=9,
            input_name=iter([None, "SDNA Std A1", "SDNA Std B1", "SDNA Std C1", "SDNA Std D1",
                             "SDNA Std E1", "SDNA Std F1", "SDNA Std G1", "SDNA Std H1"]),
            output_per_input=3,
            output_type='ResultFile',
            step_udfs={'Sample Volume (ul)': '2', 'Master Mix Volume (ul)': '198'}
        )

        with pytest.raises(InvalidStepError) as e:
            self.epp._run()
        assert e.value.message == 'SDNA Plate lot not selected. Please select in "Reagent Lot Tracking" at top of step.'
