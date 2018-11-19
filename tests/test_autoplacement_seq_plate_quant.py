import pytest

from unittest.mock import Mock, patch, PropertyMock

from EPPs.common import InvalidStepError

from scripts.autoplacement_seq_plate_quant import Autoplacement_seq_plate_quant
from tests.test_common import TestEPP, NamedMock

fake_selected_containers = [Mock(id='c1')]

#fake_input_output_maps requires the mock artifacts for input sample and input samples to have the same mock id across all three output replicates
#so create the artifacts once as input_sample_mock and input_standard_mock variables.
input_sample_mock= NamedMock(real_name="ai1_name", id='ai1',
                                               container=NamedMock(real_name='ai1_container_name'),
                                               location=('container_entity', 'A:1'))
def generate_input_output_map(number):
    mock_input_output_map=[]
    map_counter=0
    while map_counter<number:
        mock_input_output_map.append(
                                    [{'uri': NamedMock(real_name="ai"+str(map_counter)+"_name", id='ai'+str(map_counter),
                                               container=NamedMock(real_name='ai'+str(map_counter)+'_container_name'),
                                               location=('container_entity', 'A:1'))},
                         {'output-generation-type': 'PerInput', 'uri': NamedMock(real_name="ao1_name-1")}]

                                )
        map_counter += 1

    return mock_input_output_map

#generate mock input artifacts for all standards
input_SDNAA1_mock = NamedMock(real_name="SDNA Std A1", id='si1')
input_SDNAB1_mock = NamedMock(real_name="SDNA Std B1", id='si2')
input_SDNAC1_mock = NamedMock(real_name="SDNA Std C1", id='si3')
input_SDNAD1_mock = NamedMock(real_name="SDNA Std D1", id='si1')
input_SDNAE1_mock = NamedMock(real_name="SDNA Std E1", id='si1')
input_SDNAF1_mock = NamedMock(real_name="SDNA Std F1", id='si1')
input_SDNAG1_mock = NamedMock(real_name="SDNA Std G1", id='si1')
input_SDNAH1_mock = NamedMock(real_name="SDNA Std H1", id='si1')



fake_input_output_maps = [
                        [{'uri': input_sample_mock},
                         {'output-generation-type': 'PerInput', 'uri': NamedMock(real_name="ao1_name-1")}],
                        [{'uri': input_sample_mock},
                         {'output-generation-type': 'PerInput', 'uri': NamedMock(real_name="ao1_name-2")}],
                        [{'uri': input_sample_mock},
                         {'output-generation-type': 'PerInput', 'uri': NamedMock(real_name="ao1_name-3")}],
                        [{'uri': input_SDNAA1_mock},
                         {'output-generation-type': 'PerInput', 'uri': NamedMock(real_name="SDNA Std A1-1")}],
                        [{'uri': input_SDNAA1_mock},
                         {'output-generation-type': 'PerInput', 'uri': NamedMock(real_name="SDNA Std A1-2")}],
                        [{'uri': input_SDNAA1_mock},
                         {'output-generation-type': 'PerInput', 'uri': NamedMock(real_name="SDNA Std A1-3")}],
                        [{'uri': input_SDNAB1_mock},
                         {'output-generation-type': 'PerInput', 'uri': NamedMock(real_name="SDNA Std B1-1")}],
                        [{'uri': input_SDNAB1_mock},
                         {'output-generation-type': 'PerInput', 'uri': NamedMock(real_name="SDNA Std B1-2")}],
                        [{'uri': input_SDNAB1_mock},
                         {'output-generation-type': 'PerInput', 'uri': NamedMock(real_name="SDNA Std B1-3")}],
                        [{'uri': input_SDNAC1_mock},
                         {'output-generation-type': 'PerInput', 'uri': NamedMock(real_name="SDNA Std C1-1")}],
                        [{'uri': input_SDNAC1_mock},
                         {'output-generation-type': 'PerInput', 'uri': NamedMock(real_name="SDNA Std C1-2")}],
                        [{'uri': input_SDNAC1_mock},
                         {'output-generation-type': 'PerInput', 'uri': NamedMock(real_name="SDNA Std C1-3")}],
                        [{'uri': input_SDNAD1_mock},
                         {'output-generation-type': 'PerInput', 'uri': NamedMock(real_name="SDNA Std D1-1")}],
                        [{'uri': input_SDNAD1_mock},
                         {'output-generation-type': 'PerInput', 'uri': NamedMock(real_name="SDNA Std D1-2")}],
                        [{'uri': input_SDNAD1_mock},
                         {'output-generation-type': 'PerInput', 'uri': NamedMock(real_name="SDNA Std D1-3")}],
                        [{'uri': input_SDNAE1_mock},
                         {'output-generation-type': 'PerInput', 'uri': NamedMock(real_name="SDNA Std E1-1")}],
                        [{'uri': input_SDNAE1_mock},
                         {'output-generation-type': 'PerInput', 'uri': NamedMock(real_name="SDNA Std E1-2")}],
                        [{'uri': input_SDNAE1_mock},
                         {'output-generation-type': 'PerInput', 'uri': NamedMock(real_name="SDNA Std E1-3")}],
                        [{'uri': input_SDNAF1_mock},
                         {'output-generation-type': 'PerInput', 'uri': NamedMock(real_name="SDNA Std F1-1")}],
                        [{'uri': input_SDNAF1_mock},
                         {'output-generation-type': 'PerInput', 'uri': NamedMock(real_name="SDNA Std F1-2")}],
                        [{'uri': input_SDNAF1_mock},
                         {'output-generation-type': 'PerInput', 'uri': NamedMock(real_name="SDNA Std F1-3")}],
                        [{'uri': input_SDNAG1_mock},
                         {'output-generation-type': 'PerInput', 'uri': NamedMock(real_name="SDNA Std G1-1")}],
                        [{'uri': input_SDNAG1_mock},
                         {'output-generation-type': 'PerInput', 'uri': NamedMock(real_name="SDNA Std G1-2")}],
                        [{'uri': input_SDNAG1_mock},
                         {'output-generation-type': 'PerInput', 'uri': NamedMock(real_name="SDNA Std G1-3")}],
                        [{'uri': input_SDNAH1_mock},
                         {'output-generation-type': 'PerInput', 'uri': NamedMock(real_name="SDNA Std H1-1")}],
                        [{'uri': input_SDNAH1_mock},
                         {'output-generation-type': 'PerInput', 'uri': NamedMock(real_name="SDNA Std H1-2")}],
                        [{'uri': input_SDNAH1_mock},
                         {'output-generation-type': 'PerInput', 'uri': NamedMock(real_name="SDNA Std H1-3")}]

                        ]

fake_input_output_maps2 = [
                        [{'uri': input_sample_mock},
                         {'output-generation-type': 'PerInput', 'uri': NamedMock(real_name="ao1_name-1")}]
                        ]

fake_input_output_maps3 = [
                        [{'uri': input_SDNAA1_mock},
                         {'output-generation-type': 'PerInput', 'uri': NamedMock(real_name="SDNA Std A1-1")}],
                        [{'uri': input_SDNAA1_mock},
                         {'output-generation-type': 'PerInput', 'uri': NamedMock(real_name="SDNA Std A1-2")}],
                        [{'uri': input_SDNAA1_mock},
                         {'output-generation-type': 'PerInput', 'uri': NamedMock(real_name="SDNA Std A1-3")}]
                        ]
#generate 33 fake inputs for testing error raising when too many inputs
def fake_input_output_maps4():
    return generate_input_output_map(33)

class TestAutoplacementSeqPlateQuant(TestEPP):
    def setUp(self):

        self.patched_process1 = patch.object(
            Autoplacement_seq_plate_quant,
            'process',
            new_callable=PropertyMock(
                return_value=Mock(
                    input_output_maps=fake_input_output_maps,
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
                    input_output_maps=fake_input_output_maps2,
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
                    input_output_maps=fake_input_output_maps3,
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
                    input_output_maps=fake_input_output_maps4(),
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
        # per input
        with self.patched_process1, self.patched_lims:
            self.epp._run()

            expected_output_placement_list = [
                (fake_input_output_maps[3][1]['uri'], (fake_selected_containers[0], 'A:1')),
                (fake_input_output_maps[6][1]['uri'], (fake_selected_containers[0], 'B:1')),
                (fake_input_output_maps[9][1]['uri'], (fake_selected_containers[0], 'C:1')),
                (fake_input_output_maps[12][1]['uri'], (fake_selected_containers[0], 'D:1')),
                (fake_input_output_maps[15][1]['uri'], (fake_selected_containers[0], 'E:1')),
                (fake_input_output_maps[18][1]['uri'], (fake_selected_containers[0], 'F:1')),
                (fake_input_output_maps[21][1]['uri'], (fake_selected_containers[0], 'G:1')),
                (fake_input_output_maps[24][1]['uri'], (fake_selected_containers[0], 'H:1')),
                (fake_input_output_maps[4][1]['uri'], (fake_selected_containers[0], 'A:2')),
                (fake_input_output_maps[7][1]['uri'], (fake_selected_containers[0], 'B:2')),
                (fake_input_output_maps[10][1]['uri'], (fake_selected_containers[0], 'C:2')),
                (fake_input_output_maps[13][1]['uri'], (fake_selected_containers[0], 'D:2')),
                (fake_input_output_maps[16][1]['uri'], (fake_selected_containers[0], 'E:2')),
                (fake_input_output_maps[19][1]['uri'], (fake_selected_containers[0], 'F:2')),
                (fake_input_output_maps[22][1]['uri'], (fake_selected_containers[0], 'G:2')),
                (fake_input_output_maps[25][1]['uri'], (fake_selected_containers[0], 'H:2')),
                (fake_input_output_maps[5][1]['uri'], (fake_selected_containers[0], 'A:3')),
                (fake_input_output_maps[8][1]['uri'], (fake_selected_containers[0], 'B:3')),
                (fake_input_output_maps[11][1]['uri'], (fake_selected_containers[0], 'C:3')),
                (fake_input_output_maps[14][1]['uri'], (fake_selected_containers[0], 'D:3')),
                (fake_input_output_maps[17][1]['uri'], (fake_selected_containers[0], 'E:3')),
                (fake_input_output_maps[20][1]['uri'], (fake_selected_containers[0], 'F:3')),
                (fake_input_output_maps[23][1]['uri'], (fake_selected_containers[0], 'G:3')),
                (fake_input_output_maps[26][1]['uri'], (fake_selected_containers[0], 'H:3')),
                (fake_input_output_maps[0][1]['uri'], (fake_selected_containers[0], 'A:4')),
                (fake_input_output_maps[1][1]['uri'], (fake_selected_containers[0], 'A:5')),
                (fake_input_output_maps[2][1]['uri'], (fake_selected_containers[0], 'A:6'))
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
             assert e.value.message =='Maximum number of inputs is 32. 33 inputs present in step'
