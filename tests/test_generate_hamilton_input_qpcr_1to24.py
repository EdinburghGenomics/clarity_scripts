
import pytest
from pyclarity_lims.entities import ReagentLot

from EPPs.common import InvalidStepError

from scripts.generate_hamilton_input_qpcr_1to24 import GenerateHamiltonInputQPCR
from tests.test_common import TestEPP, FakeEntitiesMaker


class TestGenerateHamiltonInputQPCR(TestEPP):
    def setUp(self):
        self.epp = GenerateHamiltonInputQPCR(self.default_argv + ['-i', 'a_file_location'] + ['-d', self.assets])

    def test_happy_input(self):  # test that file is written under happy path conditions i.e. 1 input plate, 1 output
        # per input, 1 output plate
        fem = FakeEntitiesMaker()
        self.epp.lims = fem.lims
        self.epp.process = fem.create_a_fake_process(
            nb_input=9,
            # Input name as None means they are automatically generated
            input_name=iter([None, None, 'QSTD A1', 'QSTD B1', 'QSTD C1', 'QSTD D1', 'QSTD E1', 'QSTD F1', 'No Template Control']),
            nb_input_container=8,
            input_container_type=iter(['96 well plate'] + ['Tube'] * 7),
            # This will put 2 artifact in the first container then one in the followings
            input_container_population_patterns=[2, 1, 1, 1, 1, 1, 1,1],
            output_per_input=3,
            output_type='ResultFile',
            step_udfs={'DIL1 Plate Barcode': 'LP9999999-DIL1', 'DIL2 Plate Barcode': 'LP9999999-DIL2'},
        )
        # Set the reagent lots
        self.epp.process.step._reagent_lots.reagent_lots = [
            fem.create_instance(ReagentLot, id='re1', lot_number='LP9999999-QSTD'),
            fem.create_instance(ReagentLot, id='re2', lot_number='LP9999999-QMX')
        ]
        self.epp._run()
        expected_lines = [
            ','.join(self.epp.csv_column_headers),
            'input_art_A:1,input_uri_container_1,A1,output_uri_container_9,A1,B1,C1,LP9999999-DIL1,LP9999999-DIL2,LP9999999-QSTD,LP9999999-QMX',
            'input_art_B:1,input_uri_container_1,B1,output_uri_container_9,D1,E1,F1,LP9999999-DIL1,LP9999999-DIL2,LP9999999-QSTD,LP9999999-QMX',
            'QSTD A1,input_uri_container_2,11,output_uri_container_9,A2,G1,H1,LP9999999-DIL1,LP9999999-DIL2,LP9999999-QSTD,LP9999999-QMX',
            'QSTD B1,input_uri_container_3,11,output_uri_container_9,B2,C2,D2,LP9999999-DIL1,LP9999999-DIL2,LP9999999-QSTD,LP9999999-QMX',
            'QSTD C1,input_uri_container_4,11,output_uri_container_9,E2,F2,G2,LP9999999-DIL1,LP9999999-DIL2,LP9999999-QSTD,LP9999999-QMX',
            'QSTD D1,input_uri_container_5,11,output_uri_container_9,A3,B3,H2,LP9999999-DIL1,LP9999999-DIL2,LP9999999-QSTD,LP9999999-QMX',
            'QSTD E1,input_uri_container_6,11,output_uri_container_9,C3,D3,E3,LP9999999-DIL1,LP9999999-DIL2,LP9999999-QSTD,LP9999999-QMX',
            'QSTD F1,input_uri_container_7,11,output_uri_container_9,F3,G3,H3,LP9999999-DIL1,LP9999999-DIL2,LP9999999-QSTD,LP9999999-QMX',
            'No Template Control,input_uri_container_8,11,output_uri_container_9,A4,B4,C4,LP9999999-DIL1,LP9999999-DIL2,LP9999999-QSTD,LP9999999-QMX',
        ]


        assert self.file_content('a_file_location-hamilton_input.csv') == expected_lines
        assert self.stripped_md5('a_file_location-hamilton_input.csv') == '2e8887dca0ee617474a38ee8e3e29516'
        assert self.stripped_md5(self.epp.shared_drive_file_path) == '2e8887dca0ee617474a38ee8e3e29516'

    def test_2_output_artifacts(self):  # test that error occurs if not 3 output artifacts for one input
        fem = FakeEntitiesMaker()
        self.epp.lims = fem.lims
        self.epp.process = fem.create_a_fake_process(
            nb_input=8,
            input_name=iter(
                [None, None, 'QSTD A1', 'QSTD B1', 'QSTD C1', 'QSTD D1', 'QSTD E1', 'QSTD F1', 'No Template Control']),
            nb_input_container=7,
            input_container_type=iter(['96 well plate'] + ['Tube'] * 6),
            input_container_population_patterns=[2, 1, 1, 1, 1, 1, 1],
            output_per_input=2,  # <--- Only 2 outputs per input
            output_type='ResultFile',
            step_udfs={'DIL1 Plate Barcode': 'LP9999999-DIL1', 'DIL2 Plate Barcode': 'LP9999999-DIL2'},
        )
        # Set the reagent lots
        self.epp.process.step._reagent_lots.reagent_lots = [
            fem.create_instance(ReagentLot, id='re1', lot_number='LP9999999-QSTD'),
            fem.create_instance(ReagentLot, id='re2', lot_number='LP9999999-QMX')
        ]
        with pytest.raises(InvalidStepError) as e:
            self.epp._run()
        assert e.value.message == '2 outputs found for an input input_art_A:1. 3 replicates required.'

    def test_not_DIL1(self):  # test that sys exit occurs if DIL1 barcode does not have correct format
        fem = FakeEntitiesMaker()
        self.epp.lims = fem.lims
        self.epp.process = fem.create_a_fake_process(
            nb_input=8,
            input_name=iter(
                [None, None, 'QSTD A1', 'QSTD B1', 'QSTD C1', 'QSTD D1', 'QSTD E1', 'QSTD F1', 'No Template Control']),
            nb_input_container=7,
            input_container_type=iter(['96 well plate'] + ['Tube'] * 6),
            input_container_population_patterns=[2, 1, 1, 1, 1, 1, 1],
            output_per_input=3,
            output_type='ResultFile',
            step_udfs={'DIL1 Plate Barcode': 'LP9999999-DOT1', 'DIL2 Plate Barcode': 'LP9999999-DIL2'},
        )
        # Set the reagent lots
        self.epp.process.step._reagent_lots.reagent_lots = [
            fem.create_instance(ReagentLot, id='re1', lot_number='LP9999999-QSTD'),
            fem.create_instance(ReagentLot, id='re2', lot_number='LP9999999-QMX')
        ]

        with pytest.raises(InvalidStepError) as e:
            self.epp._run()
        assert e.value.message == 'LP9999999-DOT1 is not a valid DIL1 container name. Container names must match LP[0-9]{7}-DIL1'

    def test_not_DIL2(self):  # test that sys exit occurs if DIL2 barcode does not have correct format
        fem = FakeEntitiesMaker()
        self.epp.lims = fem.lims
        self.epp.process = fem.create_a_fake_process(
            nb_input=8,
            input_name=iter(
                [None, None, 'QSTD A1', 'QSTD B1', 'QSTD C1', 'QSTD D1', 'QSTD E1', 'QSTD F1', 'No Template Control']),
            nb_input_container=7,
            input_container_type=iter(['96 well plate'] + ['Tube'] * 6),
            input_container_population_patterns=[2, 1, 1, 1, 1, 1, 1],
            output_per_input=3,  # <--- Only 2 outputs per input
            output_type='ResultFile',
            step_udfs={'DIL1 Plate Barcode': 'LP9999999-DIL1', 'DIL2 Plate Barcode': 'LP9999999-DOT2'},
        )
        # Set the reagent lots
        self.epp.process.step._reagent_lots.reagent_lots = [
            fem.create_instance(ReagentLot, id='re1', lot_number='LP9999999-QSTD'),
            fem.create_instance(ReagentLot, id='re2', lot_number='LP9999999-QMX')
        ]

        with pytest.raises(InvalidStepError) as e:
            self.epp._run()
        assert e.value.message == 'LP9999999-DOT2 is not a valid DIL2 container name. Container names must match LP[0-9]{7}-DIL2'
