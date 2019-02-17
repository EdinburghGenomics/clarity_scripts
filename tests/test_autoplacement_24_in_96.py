from unittest.mock import Mock, patch, PropertyMock

from pyclarity_lims.entities import Step

from scripts.autoplacement_24_in_96 import Autoplacement24in96
from tests.test_common import TestEPP, FakeEntitiesMaker

fake_selected_containers = [Mock(id='c1')]
fake_outputs_per_input = [Mock(id='ao1', container='Container1', location='')]


class TestAutoplacement24in96(TestEPP):
    def setUp(self):
        fake_inputs = [
            Mock(id='ai1', type='Analyte', container='container', location=('container', 'A:1'),
                 output=[Mock(id='ao1', type='Analyte', container='Container1', location=('container', ''))]),
            Mock(id='ai2', type='Analyte', container='container', location=('container', 'B:1'),
                 output=[Mock(id='ao2', type='Analyte', container='Container1', location=('container', ''))])

        ]

        self.patched_process1 = patch.object(
            Autoplacement24in96,
            'process',
            new_callable=PropertyMock(
                return_value=Mock(
                    all_inputs=Mock(return_value=fake_inputs),
                    outputs_per_input=Mock(return_value=fake_outputs_per_input),
                    step=Mock(
                        id='s1',
                        placements=Mock(id='p1', get_selected_containers=Mock(return_value=fake_selected_containers))
                    )
                )
            )
        )

        self.patched_lims = patch.object(Autoplacement24in96, 'lims', new_callable=PropertyMock)

        self.epp = Autoplacement24in96(
            self.default_argv)

    def test_autoplacement_24_in_96(self):
        # per input
        fem = FakeEntitiesMaker()
        self.epp.lims = fem.lims
        self.epp.process = fem.create_a_fake_process(nb_input=24)
        patch_step_set_placement = patch.object(Step, 'set_placements')
        with patch_step_set_placement as mock_set_placements:
            self.epp._run()
        print(mock_set_placements.mock_calls)
        
        # these are the output containers
        fake_output_container = fem.object_store_per_type.get('Container')[1]
        # these are the output artifacts
        fake_outputs_artifacts = fem.object_store_per_type.get('Artifact')[24:]
        exp_placements = [
            (fake_outputs_artifacts[0], (fake_output_container, 'A:1')),
            (fake_outputs_artifacts[1], (fake_output_container, 'B:1')),
            (fake_outputs_artifacts[2], (fake_output_container, 'C:1')),
            (fake_outputs_artifacts[3], (fake_output_container, 'D:1')),
            (fake_outputs_artifacts[4], (fake_output_container, 'E:1')),
            (fake_outputs_artifacts[5], (fake_output_container, 'F:1')),
            (fake_outputs_artifacts[6], (fake_output_container, 'G:1')),
            (fake_outputs_artifacts[7], (fake_output_container, 'H:1')),
            (fake_outputs_artifacts[8], (fake_output_container, 'A:2')),
            (fake_outputs_artifacts[9], (fake_output_container, 'B:2')),
            (fake_outputs_artifacts[10], (fake_output_container, 'C:2')),
            (fake_outputs_artifacts[11], (fake_output_container, 'D:2')),
            (fake_outputs_artifacts[12], (fake_output_container, 'E:2')),
            (fake_outputs_artifacts[13], (fake_output_container, 'F:2')),
            (fake_outputs_artifacts[14], (fake_output_container, 'G:2')),
            (fake_outputs_artifacts[15], (fake_output_container, 'H:2')),
            (fake_outputs_artifacts[16], (fake_output_container, 'A:3')),
            (fake_outputs_artifacts[17], (fake_output_container, 'B:3')),
            (fake_outputs_artifacts[18], (fake_output_container, 'C:3')),
            (fake_outputs_artifacts[19], (fake_output_container, 'D:3')),
            (fake_outputs_artifacts[20], (fake_output_container, 'E:3')),
            (fake_outputs_artifacts[21], (fake_output_container, 'F:3'))
        ]
        print(exp_placements)
        print(mock_set_placements.mock_calls[0][1][1])
        #mock_set_placements.assert_called_with([fake_output_container], exp_placements)

        # with self.patched_process1, self.patched_lims:
        #     self.epp._run()
        #
        #     expected_output_placement = [
        #         (fake_outputs_per_input[0], (fake_selected_containers[0], 'A:1')),
        #         (fake_outputs_per_input[0], (fake_selected_containers[0], 'B:1'))
        #     ]
        #     self.epp.process.step.set_placements.assert_called_with(fake_selected_containers, expected_output_placement)

