from unittest.mock import Mock, patch, PropertyMock

from scripts.autoplacement_24_in_96 import Autoplacement24in96
from tests.test_common import TestEPP

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
        with self.patched_process1, self.patched_lims:
            self.epp._run()

            expected_output_placement = [
                (fake_outputs_per_input[0], (fake_selected_containers[0], 'A:1')),
                (fake_outputs_per_input[0], (fake_selected_containers[0], 'B:1'))
            ]
            self.epp.process.step.set_placements.assert_called_with(fake_selected_containers, expected_output_placement)

