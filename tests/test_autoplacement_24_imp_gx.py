from unittest.mock import patch
from pyclarity_lims.entities import Container, Step

from scripts.autoplacement_24_imp_gx import Autoplacement24IMPGX
from tests.test_common import TestEPP, FakeEntitiesMaker


class TestAutoplacement24IMPGX(TestEPP):
    def setUp(self):
        self.epp = Autoplacement24IMPGX(self.default_argv)

    def test_autoplacement_qPCR_384_happy_path(self):
        fem = FakeEntitiesMaker()
        self.epp.process = fem.create_a_fake_process(nb_input=2, output_per_input=2)
        self.epp.lims = fem.lims
        patch_container_create = patch.object(
            Container,
            'create',
            return_value=fem.create_a_fake_container(container_type="384 well plate", is_output_container=True)
        )
        patch_step_set_placement = patch.object(Step, 'set_placements')
        with patch_container_create, patch_step_set_placement as mock_set_placements:
            self.epp._run()
        # these are the output containers
        fake_output_containers = fem.object_store_per_type.get('Container')[1:]
        # these are the output artifacts
        fake_outputs_artifacts = fem.object_store_per_type.get('Artifact')[2:]
        expected_output_placement = [
            (fake_outputs_artifacts[0], (fake_output_containers[0], 'A:1')),
            (fake_outputs_artifacts[1], (fake_output_containers[1], 'A:1')),
            (fake_outputs_artifacts[2], (fake_output_containers[0], 'B:1')),
            (fake_outputs_artifacts[3], (fake_output_containers[1], 'C:1')),
        ]
        mock_set_placements.assert_called_once_with(fake_output_containers, expected_output_placement)

