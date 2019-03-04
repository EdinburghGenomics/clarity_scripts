from unittest.mock import Mock, patch, PropertyMock

import pytest
from pyclarity_lims.entities import Step

from EPPs.common import InvalidStepError
from scripts.autoplacement_qpcr_384 import AutoplacementQPCR384
from tests.test_common import TestEPP, NamedMock, FakeEntitiesMaker


class TestAutoplacementQPCR384(TestEPP):
    def setUp(self):
        self.epp = AutoplacementQPCR384(
            self.default_argv)

    def test_autoplacement_qPCR_384_happy_path(self):
        # per input
        fem = FakeEntitiesMaker()
        self.epp.lims = fem.lims
        self.epp.process = fem.create_a_fake_process(
            nb_input=8,
            input_name=iter(["ai1 name", "QSTD A", "QSTD B", "QSTD C", "QSTD D", "QSTD E", "QSTD F", "No Template Control"]),
            output_per_input=3,
            output_type='ResultFile'
        )
        patch_step_set_placement = patch.object(Step, 'set_placements')
        with patch_step_set_placement as mock_set_placements:
            self.epp._validate_step()
            self.epp._run()
        # these are the output containers
        fake_output_container = fem.object_store_per_type.get('Container')[1]
        # these are the output artifacts
        fake_outputs_artifacts = fem.object_store_per_type.get('Artifact')[8:]
        # placement starts with QSTD and finishes with input
        expected_output_placement = [
            (fake_outputs_artifacts[3], (fake_output_container, 'A:1')),
            (fake_outputs_artifacts[4], (fake_output_container, 'A:3')),
            (fake_outputs_artifacts[5], (fake_output_container, 'A:5')),
            (fake_outputs_artifacts[6], (fake_output_container, 'C:1')),
            (fake_outputs_artifacts[7], (fake_output_container, 'C:3')),
            (fake_outputs_artifacts[8], (fake_output_container, 'C:5')),
            (fake_outputs_artifacts[9], (fake_output_container, 'E:1')),
            (fake_outputs_artifacts[10], (fake_output_container, 'E:3')),
            (fake_outputs_artifacts[11], (fake_output_container, 'E:5')),
            (fake_outputs_artifacts[12], (fake_output_container, 'G:1')),
            (fake_outputs_artifacts[13], (fake_output_container, 'G:3')),
            (fake_outputs_artifacts[14], (fake_output_container, 'G:5')),
            (fake_outputs_artifacts[15], (fake_output_container, 'I:1')),
            (fake_outputs_artifacts[16], (fake_output_container, 'I:3')),
            (fake_outputs_artifacts[17], (fake_output_container, 'I:5')),
            (fake_outputs_artifacts[18], (fake_output_container, 'K:1')),
            (fake_outputs_artifacts[19], (fake_output_container, 'K:3')),
            (fake_outputs_artifacts[20], (fake_output_container, 'K:5')),
            (fake_outputs_artifacts[21], (fake_output_container, 'M:1')),
            (fake_outputs_artifacts[22], (fake_output_container, 'M:3')),
            (fake_outputs_artifacts[23], (fake_output_container, 'M:5')),
            (fake_outputs_artifacts[0], (fake_output_container, 'B:1')),
            (fake_outputs_artifacts[1], (fake_output_container, 'A:2')),
            (fake_outputs_artifacts[2], (fake_output_container, 'B:2'))
        ]

        mock_set_placements.assert_called_with([fake_output_container], expected_output_placement)

    def test_autoplacement_qPCR_384_1_QSTD(self):  # Only 1 QSTD
        fem = FakeEntitiesMaker()
        self.epp.lims = fem.lims
        self.epp.process = fem.create_a_fake_process(
            nb_input=2,
            input_name=iter(["ai1 name", "QSTD A"]),
            output_per_input=3,
            output_type='ResultFile'
        )
        self.epp._validate_step()
        with pytest.raises(InvalidStepError) as e:
            self.epp._run()
        assert e.value.message == 'Step requires QSTD A to F and No Template Control with 3 replicates each'
