from unittest.mock import Mock, patch, PropertyMock

import pytest
from EPPs.common import InvalidStepError

from scripts.autoplacement_seq_plate_quant import AutoplacementSeqPlateQuant
from tests.test_common import TestEPP, NamedMock

fake_selected_containers = [Mock(id='c1')]

# fake_input_output_maps requires the mock artifacts for input sample and input samples to have the same mock id across all three output replicates
# so create the artifacts once as input_sample_mock and input_standard_mock variables.
input_sample_mock = NamedMock(real_name="ai1_name", id='ai1',
                              container=NamedMock(real_name='ai1_container_name'),
                              location=('container_entity', 'A:1'))


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


# generate mock input artifacts for all standards
input_SDNAA1_mock = NamedMock(real_name="SDNA Std A1", id='sA1')
input_SDNAB1_mock = NamedMock(real_name="SDNA Std B1", id='sB1')
input_SDNAC1_mock = NamedMock(real_name="SDNA Std C1", id='sC1')
input_SDNAD1_mock = NamedMock(real_name="SDNA Std D1", id='sD1')
input_SDNAE1_mock = NamedMock(real_name="SDNA Std E1", id='sE1')
input_SDNAF1_mock = NamedMock(real_name="SDNA Std F1", id='sF1')
input_SDNAG1_mock = NamedMock(real_name="SDNA Std G1", id='sG1')
input_SDNAH1_mock = NamedMock(real_name="SDNA Std H1", id='sH1')


def fake_all_inputs(unique=False, resolve=False):
    return (input_sample_mock,
            input_SDNAA1_mock,
            input_SDNAB1_mock,
            input_SDNAC1_mock,
            input_SDNAD1_mock,
            input_SDNAE1_mock,
            input_SDNAF1_mock,
            input_SDNAG1_mock,
            input_SDNAH1_mock)


# only 1 standard, not the required 8
def fake_all_inputs2(unique=False, resolve=False):
    return (input_sample_mock,
            input_SDNAA1_mock,
            )


# generate 33 fake inputs for testing error raising when too many inputs
def generate_fake_all_inputs(number):
    mock_fake_all_inputs = []
    map_counter = 0
    while map_counter < number:
        mock_fake_all_inputs.append(
            NamedMock(real_name="ai" + str(map_counter) + "_name", id='ai' + str(map_counter))
        )
        map_counter += 1

    return mock_fake_all_inputs


def fake_all_inputs3(unique=True):
    return generate_fake_all_inputs(33)


# happy path outputs
outputs = {

    'ai1': [NamedMock(real_name="ao1_name-1"), NamedMock(real_name="ao1_name-2"), NamedMock(real_name="ao1_name-3")],
    'sA1': [NamedMock(real_name="SDNA Std A1-1"), NamedMock(real_name="SDNA Std A1-2"),
            NamedMock(real_name="SDNA Std A1-3")],
    'sB1': [NamedMock(real_name="SDNA Std B1-1"), NamedMock(real_name="SDNA Std B1-2"),
            NamedMock(real_name="SDNA Std B1-3")],
    'sC1': [NamedMock(real_name="SDNA Std C1-1"), NamedMock(real_name="SDNA Std C1-2"),
            NamedMock(real_name="SDNA Std C1-3")],
    'sD1': [NamedMock(real_name="SDNA Std D1-1"), NamedMock(real_name="SDNA Std D1-2"),
            NamedMock(real_name="SDNA Std D1-3")],
    'sE1': [NamedMock(real_name="SDNA Std E1-1"), NamedMock(real_name="SDNA Std E1-2"),
            NamedMock(real_name="SDNA Std E1-3")],
    'sF1': [NamedMock(real_name="SDNA Std F1-1"), NamedMock(real_name="SDNA Std F1-2"),
            NamedMock(real_name="SDNA Std F1-3")],
    'sG1': [NamedMock(real_name="SDNA Std G1-1"), NamedMock(real_name="SDNA Std G1-2"),
            NamedMock(real_name="SDNA Std G1-3")],
    'sH1': [NamedMock(real_name="SDNA Std H1-1"), NamedMock(real_name="SDNA Std H1-2"),
            NamedMock(real_name="SDNA Std H1-3")]
}

# only 1 output per input not expected 3
outputs2 = {
    'ai1': [NamedMock(real_name="ao1_name-1")]
}

# only 1 standard, not the required 8
outputs3 = {
    'ai1': [NamedMock(real_name="ao1_name-1"), NamedMock(real_name="ao1_name-2"), NamedMock(real_name="ao1_name-3")],
    'sA1': [NamedMock(real_name="SDNA Std A1-1"), NamedMock(real_name="SDNA Std A1-2"),
            NamedMock(real_name="SDNA Std A1-3")]
}


def get_fake_outputs_per_input(outputs):
    def fake_outputs_per_input(inputid, ResultFile=True):
        return outputs[inputid]

    return fake_outputs_per_input


fake_input_output_maps3 = [
    [{'uri': input_SDNAA1_mock},
     {'output-generation-type': 'PerInput', 'uri': NamedMock(real_name="SDNA Std A1-1")}],
    [{'uri': input_SDNAA1_mock},
     {'output-generation-type': 'PerInput', 'uri': NamedMock(real_name="SDNA Std A1-2")}],
    [{'uri': input_SDNAA1_mock},
     {'output-generation-type': 'PerInput', 'uri': NamedMock(real_name="SDNA Std A1-3")}]
]


class TestAutoplacementSeqPlateQuant(TestEPP):
    def setUp(self):
        self.patched_process1 = patch.object(
            AutoplacementSeqPlateQuant,
            'process',
            new_callable=PropertyMock(return_value=Mock(
                all_inputs=fake_all_inputs,
                outputs_per_input=get_fake_outputs_per_input(outputs),
                step=Mock(
                    id='s1',
                    placements=Mock(id='p1', get_selected_containers=Mock(return_value=fake_selected_containers))
                )
            )
            )
        )

        self.patched_process2 = patch.object(
            AutoplacementSeqPlateQuant,
            'process',
            new_callable=PropertyMock(return_value=Mock(
                all_inputs=fake_all_inputs,
                outputs_per_input=get_fake_outputs_per_input(outputs2),
                step=Mock(
                    id='s1',
                    placements=Mock(id='p1', get_selected_containers=Mock(return_value=fake_selected_containers))
                )
            )
            )
        )

        self.patched_process3 = patch.object(
            AutoplacementSeqPlateQuant,
            'process',
            new_callable=PropertyMock(return_value=Mock(
                all_inputs=fake_all_inputs2,
                outputs_per_input=get_fake_outputs_per_input(outputs3),
                step=Mock(
                    id='s1',
                    placements=Mock(id='p1', get_selected_containers=Mock(return_value=fake_selected_containers))
                )
            )
            )
        )

        self.patched_process4 = patch.object(
            AutoplacementSeqPlateQuant,
            'process',
            new_callable=PropertyMock(return_value=Mock(
                all_inputs=fake_all_inputs3,
                outputs_per_input=get_fake_outputs_per_input(outputs),
                step=Mock(
                    id='s1',
                    placements=Mock(id='p1', get_selected_containers=Mock(return_value=fake_selected_containers))
                )
            )
            )
        )

        self.patched_lims = patch.object(AutoplacementSeqPlateQuant, 'lims', new_callable=PropertyMock)

        self.epp = AutoplacementSeqPlateQuant(
            self.default_argv)

    def test_happy_path(self):
        # per input
        with self.patched_process1, self.patched_lims:
            self.epp._run()

            expected_output_placement_list = [
                (outputs['sA1'][0], (fake_selected_containers[0], 'A:1')),
                (outputs['sB1'][0], (fake_selected_containers[0], 'B:1')),
                (outputs['sC1'][0], (fake_selected_containers[0], 'C:1')),
                (outputs['sD1'][0], (fake_selected_containers[0], 'D:1')),
                (outputs['sE1'][0], (fake_selected_containers[0], 'E:1')),
                (outputs['sF1'][0], (fake_selected_containers[0], 'F:1')),
                (outputs['sG1'][0], (fake_selected_containers[0], 'G:1')),
                (outputs['sH1'][0], (fake_selected_containers[0], 'H:1')),
                (outputs['sA1'][1], (fake_selected_containers[0], 'A:2')),
                (outputs['sB1'][1], (fake_selected_containers[0], 'B:2')),
                (outputs['sC1'][1], (fake_selected_containers[0], 'C:2')),
                (outputs['sD1'][1], (fake_selected_containers[0], 'D:2')),
                (outputs['sE1'][1], (fake_selected_containers[0], 'E:2')),
                (outputs['sF1'][1], (fake_selected_containers[0], 'F:2')),
                (outputs['sG1'][1], (fake_selected_containers[0], 'G:2')),
                (outputs['sH1'][1], (fake_selected_containers[0], 'H:2')),
                (outputs['sA1'][2], (fake_selected_containers[0], 'A:3')),
                (outputs['sB1'][2], (fake_selected_containers[0], 'B:3')),
                (outputs['sC1'][2], (fake_selected_containers[0], 'C:3')),
                (outputs['sD1'][2], (fake_selected_containers[0], 'D:3')),
                (outputs['sE1'][2], (fake_selected_containers[0], 'E:3')),
                (outputs['sF1'][2], (fake_selected_containers[0], 'F:3')),
                (outputs['sG1'][2], (fake_selected_containers[0], 'G:3')),
                (outputs['sH1'][2], (fake_selected_containers[0], 'H:3')),
                (outputs['ai1'][0], (fake_selected_containers[0], 'A:4')),
                (outputs['ai1'][1], (fake_selected_containers[0], 'A:5')),
                (outputs['ai1'][2], (fake_selected_containers[0], 'A:6'))
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
