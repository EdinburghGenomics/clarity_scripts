from unittest.mock import Mock, patch, PropertyMock

import pytest
from EPPs.common import InvalidStepError

from scripts.autoplacement_seq_plate_quant import Autoplacement_seq_plate_quant
from tests.test_common import TestEPP, NamedMock

fake_selected_containers = [Mock(id='c1')]

def generate_input_output_map(number):
    mock_input_output_map = []
    map_counter = 0
    while map_counter < number:
        mock_input_output_map.append(
            [{'uri': NamedMock(real_name="ai" + str(map_counter) + "_name", id='ai' + str(map_counter),
                               container=NamedMock(real_name='ai' + str(map_counter) + '_container_name'),
                               location=('container_entity', 'A:1'))},
             {'output-generation-type': 'PerInput', 'uri': NamedMock(real_name="ao1_name-1")}]

        )
        map_counter += 1

    return mock_input_output_map


# fake all standards and 1 sample
fake_all_inputs = [
    NamedMock(real_name="SDNA Std A1", id='si1'),
    NamedMock(real_name="SDNA Std B1", id='si2'),
    NamedMock(real_name="SDNA Std C1", id='si3'),
    NamedMock(real_name="SDNA Std D1", id='si4'),
    NamedMock(real_name="SDNA Std E1", id='si5'),
    NamedMock(real_name="SDNA Std F1", id='si6'),
    NamedMock(real_name="SDNA Std G1", id='si7'),
    NamedMock(real_name="SDNA Std H1", id='si8'),
    NamedMock(real_name="ai1_name", id='ai1', container=NamedMock(real_name='ai1_container_name'),
              location=('container_entity', 'A:1'))
]

#fake all inputs containing only 1 standard and no samples
fake_all_inputs_1_standard = [
    NamedMock(real_name="SDNA Std A1", id='si1')
]

def generate_33_inputs():
    counter = 0

    fake_33_inputs = []

    while counter < 33:
        fake_33_inputs.append(
            NamedMock(real_name="ai" + str(counter) + "_name", id='ai' + str(counter),
                      container=NamedMock(real_name='ai' + str(counter) + '_container_name'),
                      location=('container_entity', 'A:1'))

        )
        counter += 1
    return fake_33_inputs

fake_outputs_per_input = [Mock(id='ao1', container='Container1', location=''),
                          Mock(id='ao2', container='Container1', location=''),
                          Mock(id='ao3', container='Container1', location='')]

fake_outputs_per_input2 = [Mock(id='ao1', container='Container1', location='')]


class TestAutoplacementSeqPlateQuant(TestEPP):
    def setUp(self):
        self.patched_process1 = patch.object(
            Autoplacement_seq_plate_quant,
            'process',
            new_callable=PropertyMock(
                return_value=Mock(
                    all_inputs=Mock(return_value=fake_all_inputs),
                    outputs_per_input=Mock(return_value=fake_outputs_per_input),
                    step=Mock(
                        id='s1',
                        placements=Mock(id='p1', get_selected_containers=Mock(return_value=fake_selected_containers))
                    )
                )
            )
        )

        self.patched_process2 = patch.object(
            Autoplacement_seq_plate_quant,
            'process',
            new_callable=PropertyMock(
                return_value=Mock(
                    all_inputs=Mock(return_value=fake_all_inputs),
                    outputs_per_input=Mock(return_value=fake_outputs_per_input2),
                    step=Mock(
                        id='s1',
                        placements=Mock(id='p1', get_selected_containers=Mock(return_value=fake_selected_containers))
                    )
                )
            )
        )

        self.patched_process3 = patch.object(
            Autoplacement_seq_plate_quant,
            'process',
            new_callable=PropertyMock(
                return_value=Mock(
                    all_inputs=Mock(return_value=fake_all_inputs_1_standard),
                    outputs_per_input=Mock(return_value=fake_outputs_per_input),
                    step=Mock(
                        id='s1',
                        placements=Mock(id='p1', get_selected_containers=Mock(return_value=fake_selected_containers))
                    )
                )
            )
        )

        self.patched_process4 = patch.object(
            Autoplacement_seq_plate_quant,
            'process',
            new_callable=PropertyMock(
                return_value=Mock(
                    all_inputs=Mock(return_value=generate_33_inputs()),
                    outputs_per_input=Mock(return_value=fake_outputs_per_input),
                    step=Mock(
                        id='s1',
                        placements=Mock(id='p1', get_selected_containers=Mock(return_value=fake_selected_containers))
                    )
                )
            )
        )

        self.patched_lims = patch.object(Autoplacement_seq_plate_quant, 'lims', new_callable=PropertyMock)

        self.epp = Autoplacement_seq_plate_quant(
            self.default_argv)

    def test_happy_path(self):
        with self.patched_process1, self.patched_lims:
            self.epp._run()

            expected_output_placement_list = [
                (fake_outputs_per_input[0], (fake_selected_containers[0], 'A:1')),
                (fake_outputs_per_input[0], (fake_selected_containers[0], 'B:1')),
                (fake_outputs_per_input[0], (fake_selected_containers[0], 'C:1')),
                (fake_outputs_per_input[0], (fake_selected_containers[0], 'D:1')),
                (fake_outputs_per_input[0], (fake_selected_containers[0], 'E:1')),
                (fake_outputs_per_input[0], (fake_selected_containers[0], 'F:1')),
                (fake_outputs_per_input[0], (fake_selected_containers[0], 'G:1')),
                (fake_outputs_per_input[0], (fake_selected_containers[0], 'H:1')),
                (fake_outputs_per_input[1], (fake_selected_containers[0], 'A:2')),
                (fake_outputs_per_input[1], (fake_selected_containers[0], 'B:2')),
                (fake_outputs_per_input[1], (fake_selected_containers[0], 'C:2')),
                (fake_outputs_per_input[1], (fake_selected_containers[0], 'D:2')),
                (fake_outputs_per_input[1], (fake_selected_containers[0], 'E:2')),
                (fake_outputs_per_input[1], (fake_selected_containers[0], 'F:2')),
                (fake_outputs_per_input[1], (fake_selected_containers[0], 'G:2')),
                (fake_outputs_per_input[1], (fake_selected_containers[0], 'H:2')),
                (fake_outputs_per_input[2], (fake_selected_containers[0], 'A:3')),
                (fake_outputs_per_input[2], (fake_selected_containers[0], 'B:3')),
                (fake_outputs_per_input[2], (fake_selected_containers[0], 'C:3')),
                (fake_outputs_per_input[2], (fake_selected_containers[0], 'D:3')),
                (fake_outputs_per_input[2], (fake_selected_containers[0], 'E:3')),
                (fake_outputs_per_input[2], (fake_selected_containers[0], 'F:3')),
                (fake_outputs_per_input[2], (fake_selected_containers[0], 'G:3')),
                (fake_outputs_per_input[2], (fake_selected_containers[0], 'H:3')),
                (fake_outputs_per_input[0], (fake_selected_containers[0], 'A:4')),
                (fake_outputs_per_input[1], (fake_selected_containers[0], 'A:5')),
                (fake_outputs_per_input[2], (fake_selected_containers[0], 'A:6'))
            ]

            self.epp.process.step.set_placements.assert_called_with(fake_selected_containers,
                                                                    expected_output_placement_list)

    def test_only_1_replicate(self):  # only 1 replicate output rather than required 3
        # per input
        with self.patched_process2, self.patched_lims:
            with pytest.raises(InvalidStepError) as e:
                self.epp._run()

            assert e.value.message == "3 replicates required for each sample and standard. Did you remember to click 'Apply' when assigning replicates?"

    def test_only_1_standard(self):  # Only 1 QSTD
        with self.patched_process3, self.patched_lims:
            with pytest.raises(InvalidStepError) as e:
                self.epp._run()

            assert e.value.message == "Standards missing from step. All 8 standards should be added to the step."

    def test_autoplacement_33_input_samples(self):  # >24 samples plus 8 standards is 32, no more than 32 permitted
        with self.patched_process4, self.patched_lims:
            with pytest.raises(InvalidStepError) as e:
                self.epp._run()

            assert e.value.message == 'Maximum number of inputs is 32. 33 inputs present in step'
