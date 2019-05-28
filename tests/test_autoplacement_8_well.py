from unittest.mock import Mock, patch, PropertyMock

from pyclarity_lims.entities import Step

from scripts.autoplacement_8_well import Autoplacement8Well
from tests.test_common import TestEPP, FakeEntitiesMaker

fake_selected_containers = [Mock(id='c1')]
fake_outputs_per_input = [Mock(id='ao1', container='Container1', location='')]


class TestAutoplacement8Well(TestEPP):
    def setUp(self):
        self.patched_lims = patch.object(Autoplacement8Well, 'lims', new_callable=PropertyMock)

        self.epp = Autoplacement8Well(
            self.default_argv)

    def test_autoplacement_8_well(self):
        # per input
        fem = FakeEntitiesMaker()
        self.epp.lims = fem.lims
        self.epp.process = fem.create_a_fake_process(nb_input=8, nb_input_container=1,
                                                     input_container_type='Strip Tube',
                                                     output_container_type='Strip Tube')

        patch_step_set_placement = patch.object(Step, 'set_placements')
        with patch_step_set_placement as mock_set_placements:
            self.epp._run()


        # these are the output containers
        fake_output_container = fem.object_store_per_type.get('Container')[1]
        # these are the output artifacts
        fake_outputs_artifacts = fem.object_store_per_type.get('Artifact')[8:]
        # take the output artifact from first container first (even index)
        # then from the second container (odd index)
        exp_placements = [
            (fake_outputs_artifacts[0], (fake_output_container, '1:1')),
            (fake_outputs_artifacts[1], (fake_output_container, '2:1')),
            (fake_outputs_artifacts[2], (fake_output_container, '3:1')),
            (fake_outputs_artifacts[3], (fake_output_container, '4:1')),
            (fake_outputs_artifacts[4], (fake_output_container, '5:1')),
            (fake_outputs_artifacts[5], (fake_output_container, '6:1')),
            (fake_outputs_artifacts[6], (fake_output_container, '7:1')),
            (fake_outputs_artifacts[7], (fake_output_container, '8:1')),

        ]
        mock_set_placements.assert_called_with([fake_output_container], exp_placements)

