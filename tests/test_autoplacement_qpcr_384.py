from unittest.mock import Mock, patch, PropertyMock

from scripts.autoplacement_qpcr_384 import AutoplacementQPCR384
from tests.test_common import TestEPP, NamedMock

fake_selected_containers = [Mock(id='c1')]
fake_outputs_per_input = [Mock(id='ao1', container='Container1', location=''),
                          Mock(id='ao2', container='Container1', location=''),
                          Mock(id='ao3', container='Container1', location='')]

fake_outputs_per_input2 = [Mock(id='ao1', container='Container1', location=''),
                           Mock(id='ao2', container='Container1', location='')]


def fake_inputs3():
    max_inputs = 32
    input_counter = 1
    inputs_list = []
    while input_counter <= max_inputs:
        inputs_list.append(Mock(id='ai' + str(input_counter)))
        input_counter += 1

    return inputs_list


class TestAutoplacementQPCR384(TestEPP):
    def setUp(self):
        fake_inputs = [
            NamedMock(real_name="ai1 name", id='ai1', type='Analyte', container='container',
                      location=('container', 'A:1'),
                      output=[Mock(id='ao1', type='Analyte', container='Container1', location=('container', ''))]),
            NamedMock(real_name="QSTD A", id='qA', type='Analyte', container='container', location=('container', 'B:1'),
                      output=[Mock(id='ao2', type='Analyte', container='Container1', location=('container', ''))]),
            NamedMock(real_name="QSTD B", id='qB', type='Analyte', container='container', location=('container', 'B:1'),
                      output=[Mock(id='ao2', type='Analyte', container='Container1', location=('container', ''))]),
            NamedMock(real_name="QSTD C", id='qC', type='Analyte', container='container', location=('container', 'B:1'),
                      output=[Mock(id='ao2', type='Analyte', container='Container1', location=('container', ''))]),
            NamedMock(real_name="QSTD D", id='qD', type='Analyte', container='container', location=('container', 'B:1'),
                      output=[Mock(id='ao2', type='Analyte', container='Container1', location=('container', ''))]),
            NamedMock(real_name="QSTD E", id='qE', type='Analyte', container='container', location=('container', 'B:1'),
                      output=[Mock(id='ao2', type='Analyte', container='Container1', location=('container', ''))]),
            NamedMock(real_name="QSTD F", id='qF', type='Analyte', container='container', location=('container', 'B:1'),
                      output=[Mock(id='ao2', type='Analyte', container='Container1', location=('container', ''))]),
            NamedMock(real_name="No Template Control", id='t1', type='Analyte', container='container',
                      location=('container', 'B:1'),
                      output=[Mock(id='ao2', type='Analyte', container='Container1', location=('container', ''))])

        ]

        fake_inputs2 = [
            NamedMock(real_name="ai1 name", id='ai1', type='Analyte', container='container',
                      location=('container', 'A:1'),
                      output=[Mock(id='ao1', type='Analyte', container='Container1', location=('container', ''))]),
            NamedMock(real_name="QSTD A", id='qA', type='Analyte', container='container', location=('container', 'B:1'),
                      output=[Mock(id='ao2', type='Analyte', container='Container1', location=('container', ''))])
        ]

        self.patched_process1 = patch.object(
            AutoplacementQPCR384,
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

        self.patched_process2 = patch.object(
            AutoplacementQPCR384,
            'process',
            new_callable=PropertyMock(
                return_value=Mock(
                    all_inputs=Mock(return_value=fake_inputs2),
                    outputs_per_input=Mock(return_value=fake_outputs_per_input2),
                    step=Mock(
                        id='s1',
                        placements=Mock(id='p1', get_selected_containers=Mock(return_value=fake_selected_containers))
                    )
                )
            )
        )

        self.patched_process3 = patch.object(
            AutoplacementQPCR384,
            'process',
            new_callable=PropertyMock(
                return_value=Mock(
                    all_inputs=Mock(return_value=fake_inputs2),
                    outputs_per_input=Mock(return_value=fake_outputs_per_input),
                    step=Mock(
                        id='s1',
                        placements=Mock(id='p1', get_selected_containers=Mock(return_value=fake_selected_containers))
                    )
                )
            )
        )

        self.patched_process4 = patch.object(
            AutoplacementQPCR384,
            'process',
            new_callable=PropertyMock(
                return_value=Mock(
                    all_inputs=Mock(return_value=fake_inputs3()),
                    outputs_per_input=Mock(return_value=fake_outputs_per_input),
                    step=Mock(
                        id='s1',
                        placements=Mock(id='p1', get_selected_containers=Mock(return_value=fake_selected_containers))
                    )
                )
            )
        )

        self.patched_lims = patch.object(AutoplacementQPCR384, 'lims', new_callable=PropertyMock)

        self.epp = AutoplacementQPCR384(
            self.default_argv)

    def test_autoplacement_qPCR_384_happy_path(self):
        # per input
        with self.patched_process1, self.patched_lims:
            self.epp._run()

            expected_output_placement = [
                (fake_outputs_per_input[0], (fake_selected_containers[0], 'A:1')),
                (fake_outputs_per_input[1], (fake_selected_containers[0], 'A:3')),
                (fake_outputs_per_input[2], (fake_selected_containers[0], 'A:5')),
                (fake_outputs_per_input[0], (fake_selected_containers[0], 'C:1')),
                (fake_outputs_per_input[1], (fake_selected_containers[0], 'C:3')),
                (fake_outputs_per_input[2], (fake_selected_containers[0], 'C:5')),
                (fake_outputs_per_input[0], (fake_selected_containers[0], 'E:1')),
                (fake_outputs_per_input[1], (fake_selected_containers[0], 'E:3')),
                (fake_outputs_per_input[2], (fake_selected_containers[0], 'E:5')),
                (fake_outputs_per_input[0], (fake_selected_containers[0], 'G:1')),
                (fake_outputs_per_input[1], (fake_selected_containers[0], 'G:3')),
                (fake_outputs_per_input[2], (fake_selected_containers[0], 'G:5')),
                (fake_outputs_per_input[0], (fake_selected_containers[0], 'I:1')),
                (fake_outputs_per_input[1], (fake_selected_containers[0], 'I:3')),
                (fake_outputs_per_input[2], (fake_selected_containers[0], 'I:5')),
                (fake_outputs_per_input[0], (fake_selected_containers[0], 'K:1')),
                (fake_outputs_per_input[1], (fake_selected_containers[0], 'K:3')),
                (fake_outputs_per_input[2], (fake_selected_containers[0], 'K:5')),
                (fake_outputs_per_input[0], (fake_selected_containers[0], 'M:1')),
                (fake_outputs_per_input[1], (fake_selected_containers[0], 'M:3')),
                (fake_outputs_per_input[2], (fake_selected_containers[0], 'M:5')),
                (fake_outputs_per_input[0], (fake_selected_containers[0], 'B:1')),
                (fake_outputs_per_input[1], (fake_selected_containers[0], 'A:2')),
                (fake_outputs_per_input[2], (fake_selected_containers[0], 'B:2'))
            ]
            self.epp.process.step.set_placements.assert_called_with(fake_selected_containers, expected_output_placement)

    def test_autoplacement_qPCR_384_2_replicates(self):  # only 2 replicate outputs rather than required 3
        # per input
        with self.patched_process2, self.patched_lims:
            assert self.epp._run() == 1

    def test_autoplacement_qPCR_384_1_QSTD(self):  # Only 1 QSTD
        with self.patched_process3, self.patched_lims:
            assert self.epp._run() == 1


