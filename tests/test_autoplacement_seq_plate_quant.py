from itertools import cycle
from unittest.mock import patch

import pytest
from pyclarity_lims.entities import Step

from EPPs.common import InvalidStepError

from scripts.autoplacement_seq_plate_quant import AutoplacementSeqPlateQuant
from tests.test_common import TestEPP, FakeEntitiesMaker


class TestAutoplacementSeqPlateQuant(TestEPP):
    def setUp(self):
        self.epp = AutoplacementSeqPlateQuant(self.default_argv)

    def test_happy_path(self):
        fem = FakeEntitiesMaker()
        self.epp.lims = fem.lims
        self.epp.process = fem.create_a_fake_process(
            nb_input=9,     # 1 sample + 8 Standards
            input_name=cycle(['ai1'] + ['SDNA Std A%s' % (str(n + 1)) for n in range(8)]),
            nb_input_container=9,  # 1 plate + 8 tubes
            input_container_type=cycle(['96 well plate'] + ['Tube'] * 8),
            output_per_input=3,  # All output in triplicates
            output_type='ResultFile'
        )
        patch_step_set_placement = patch.object(Step, 'set_placements')
        with patch_step_set_placement as mock_set_placements:
            self.epp._run()
        expected_output_placement = [
            ('SDNA Std A1_output_1', 'A:1'), ('SDNA Std A2_output_1', 'B:1'), ('SDNA Std A3_output_1', 'C:1'),
            ('SDNA Std A4_output_1', 'D:1'), ('SDNA Std A5_output_1', 'E:1'), ('SDNA Std A6_output_1', 'F:1'),
            ('SDNA Std A7_output_1', 'G:1'), ('SDNA Std A8_output_1', 'H:1'), ('SDNA Std A1_output_2', 'A:2'),
            ('SDNA Std A2_output_2', 'B:2'), ('SDNA Std A3_output_2', 'C:2'), ('SDNA Std A4_output_2', 'D:2'),
            ('SDNA Std A5_output_2', 'E:2'), ('SDNA Std A6_output_2', 'F:2'), ('SDNA Std A7_output_2', 'G:2'),
            ('SDNA Std A8_output_2', 'H:2'), ('SDNA Std A1_output_3', 'A:3'), ('SDNA Std A2_output_3', 'B:3'),
            ('SDNA Std A3_output_3', 'C:3'), ('SDNA Std A4_output_3', 'D:3'), ('SDNA Std A5_output_3', 'E:3'),
            ('SDNA Std A6_output_3', 'F:3'), ('SDNA Std A7_output_3', 'G:3'), ('SDNA Std A8_output_3', 'H:3'),
            ('ai1_output_1', 'A:4'), ('ai1_output_2', 'A:5'), ('ai1_output_3', 'A:6')
        ]
        # Check the output artifact names as they relate to the input's one
        assert [(a.name, p) for a, (c, p) in mock_set_placements.mock_calls[0][1][1]] == expected_output_placement

    def test_only_1_replicate(self):  # only 1 replicate output rather than required 3
        self._test_replicate_per_input(1)

    def test_only_1_standard(self):  # Only 1 QSTD
        fem = FakeEntitiesMaker()
        self.epp.lims = fem.lims
        self.epp.process = fem.create_a_fake_process(
            nb_input=2,  # 1 sample + 1 Standards
            input_name=cycle(['ai1'] + ['SDNA Std A1']),
            nb_input_container=2,  # 1 plate + 1 tubes
            input_container_type=cycle(['96 well plate'] + ['Tube'] ),
            output_per_input=3,  # All output in triplicates
            output_type='ResultFile'
        )
        with pytest.raises(InvalidStepError) as e:
            self.epp._run()
        assert e.value.message == "Standards missing from step. All 8 standards should be added to the step."

    def test_autoplacement_33_input_samples(self):  # >24 samples plus 8 standards is 32, no more than 32 permitted
        self._test_max_nb_input(33)
