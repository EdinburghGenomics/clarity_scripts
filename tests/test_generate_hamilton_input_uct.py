import pytest
from EPPs.common import InvalidStepError

from scripts.generate_hamilton_input_uct import GenerateHamiltonInputUCT
from tests.test_common import TestEPP, FakeEntitiesMaker



class TestGenerateHamiltonInputUCT(TestEPP):
    def setUp(self):
        self.epp = GenerateHamiltonInputUCT(self.default_argv + ['-i', 'an_imp_file_location'] + ['-d', ''])

    def test_happy_input(self):  # test that file is written under happy path conditions i.e. 1 input plate, 1 output
        # per input, 1 output plate
        fem = FakeEntitiesMaker()
        self.epp.lims = fem.lims
        self.epp.process = fem.create_a_fake_process(
            nb_input=2,
            output_reagent_label='A1_TATAGCCT_ATTACTCG (TATAGCCT_ATTACTCG)'
        )
        self.epp._run()
        expected_lines = [
            'Input Plate,Input Well,Sample Name,Adapter Well',
            'input_uri_container_1,A1,input_art_A:1,A1',
            'input_uri_container_1,B1,input_art_B:1,A1'
        ]

        assert self.file_content('an_imp_file_location-hamilton_input.csv') == expected_lines
        assert self.stripped_md5('an_imp_file_location-hamilton_input.csv') == '4abbc62fd9e6abe4cc94acfbc3ea03fa'

    def test_2_output_artifacts(self):  # test that sys exit occurs if >1 output artifacts for one input
        fem = FakeEntitiesMaker()
        self.epp.lims = fem.lims
        self.epp.process = fem.create_a_fake_process(
            nb_input=2,
            output_per_input=2,
            output_reagent_label='A1_TATAGCCT_ATTACTCG (TATAGCCT_ATTACTCG)'
        )
        with pytest.raises(InvalidStepError) as e:
            self.epp._run()
        assert e.value.message == 'Multiple outputs found for an input input_art_A:1. This step is not compatible with replicates.'
