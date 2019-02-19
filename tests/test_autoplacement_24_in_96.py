from unittest.mock import Mock, patch, PropertyMock

from pyclarity_lims.entities import Step

from scripts.autoplacement_24_in_96 import Autoplacement24in96
from tests.test_common import TestEPP, FakeEntitiesMaker

fake_selected_containers = [Mock(id='c1')]
fake_outputs_per_input = [Mock(id='ao1', container='Container1', location='')]


class TestAutoplacement24in96(TestEPP):
    def setUp(self):
        self.patched_lims = patch.object(Autoplacement24in96, 'lims', new_callable=PropertyMock)

        self.epp = Autoplacement24in96(
            self.default_argv)

    def test_autoplacement_24_in_96(self):
        # per input
        fem = FakeEntitiesMaker()
        self.epp.lims = fem.lims
        self.epp.process = fem.create_a_fake_process(nb_input=24, nb_input_container=2)
        # FakeEntitiesMaker places the 24 input in the two containers cycling from on to the other.
        patch_step_set_placement = patch.object(Step, 'set_placements')
        with patch_step_set_placement as mock_set_placements:
            self.epp._run()

        # these are the output containers
        fake_output_container = fem.object_store_per_type.get('Container')[2]
        # these are the output artifacts
        fake_outputs_artifacts = fem.object_store_per_type.get('Artifact')[24:]
        # take the output artifact from first container first (even index)
        # then from the second container (odd index)
        exp_placements = [
            (fake_outputs_artifacts[0], (fake_output_container, 'A:1')),
            (fake_outputs_artifacts[2], (fake_output_container, 'B:1')),
            (fake_outputs_artifacts[4], (fake_output_container, 'C:1')),
            (fake_outputs_artifacts[6], (fake_output_container, 'D:1')),
            (fake_outputs_artifacts[8], (fake_output_container, 'E:1')),
            (fake_outputs_artifacts[10], (fake_output_container, 'F:1')),
            (fake_outputs_artifacts[12], (fake_output_container, 'G:1')),
            (fake_outputs_artifacts[14], (fake_output_container, 'H:1')),
            (fake_outputs_artifacts[16], (fake_output_container, 'A:2')),
            (fake_outputs_artifacts[18], (fake_output_container, 'B:2')),
            (fake_outputs_artifacts[20], (fake_output_container, 'C:2')),
            (fake_outputs_artifacts[22], (fake_output_container, 'D:2')),
            (fake_outputs_artifacts[1], (fake_output_container, 'E:2')),
            (fake_outputs_artifacts[3], (fake_output_container, 'F:2')),
            (fake_outputs_artifacts[5], (fake_output_container, 'G:2')),
            (fake_outputs_artifacts[7], (fake_output_container, 'H:2')),
            (fake_outputs_artifacts[9], (fake_output_container, 'A:3')),
            (fake_outputs_artifacts[11], (fake_output_container, 'B:3')),
            (fake_outputs_artifacts[13], (fake_output_container, 'C:3')),
            (fake_outputs_artifacts[15], (fake_output_container, 'D:3')),
            (fake_outputs_artifacts[17], (fake_output_container, 'E:3')),
            (fake_outputs_artifacts[19], (fake_output_container, 'F:3')),
            (fake_outputs_artifacts[21], (fake_output_container, 'G:3')),
            (fake_outputs_artifacts[23], (fake_output_container, 'H:3'))
        ]
        mock_set_placements.assert_called_with([fake_output_container], exp_placements)

