from unittest.mock import Mock, patch, PropertyMock

import pytest
from EPPs.common import InvalidStepError

from scripts.generate_hamilton_input_seq_quant_plate import GenerateHamiltonInputSeqQuantPlate
from tests.test_common import TestEPP, NamedMock

# generate mock input for 1 sample
input_sample_mock = NamedMock(real_name="ai1_name", id='ai1',
                              container=NamedMock(real_name='ai1_container_name'),
                              location=(NamedMock(real_name='ai1_container_name'), 'A:1'))

# generate mock outputs for 1 sample with 3 replicates
output1_sample_mock = NamedMock(real_name="ao1_name-1", container=NamedMock(real_name='OutputContainer1'),
                                location=(NamedMock(real_name="OutputContainer1"), 'A:4'))
output2_sample_mock = NamedMock(real_name="ao1_name-1", container=NamedMock(real_name='OutputContainer1'),
                                location=(NamedMock(real_name="OutputContainer1"), 'A:5'))
output3_sample_mock = NamedMock(real_name="ao1_name-1", container=NamedMock(real_name='OutputContainer1'),
                                location=(NamedMock(real_name="OutputContainer1"), 'A:6'))
# generate a mock output with another container name for testing the number of containers present
output1b_sample_mock = NamedMock(real_name="ao1_name-1", container=NamedMock(real_name='OutputContainer2'),
                                 location=(NamedMock(real_name="OutputContainer1"), 'A:4'))

# generate mock input artifacts for all standards
input_SDNAA1_mock = NamedMock(real_name="SDNA Std A1", id='sa1', container=NamedMock(real_name='stds_container_name'),
                              location=(NamedMock(real_name='stds_container_name'), '1:1'))
input_SDNAB1_mock = NamedMock(real_name="SDNA Std B1", id='sb1',
                              container=NamedMock(real_name=NamedMock(real_name='stds_container_name')),
                              location=(NamedMock(real_name='stds_container_name'), '1:1'))
input_SDNAC1_mock = NamedMock(real_name="SDNA Std C1", id='sc1', container=NamedMock(real_name='stds_container_name'),
                              location=(NamedMock(real_name='stds_container_name'), '1:1'))
input_SDNAD1_mock = NamedMock(real_name="SDNA Std D1", id='sd1', container=NamedMock(real_name='stds_container_name'),
                              location=(NamedMock(real_name='stds_container_name'), '1:1'))
input_SDNAE1_mock = NamedMock(real_name="SDNA Std E1", id='se1', container=NamedMock(real_name='stds_container_name'),
                              location=(NamedMock(real_name='stds_container_name'), '1:1'))
input_SDNAF1_mock = NamedMock(real_name="SDNA Std F1", id='sf1', container=NamedMock(real_name='stds_container_name'),
                              location=(NamedMock(real_name='stds_container_name'), '1:1'))
input_SDNAG1_mock = NamedMock(real_name="SDNA Std G1", id='sg1', container=NamedMock(real_name='stds_container_name'),
                              location=(NamedMock(real_name='stds_container_name'), '1:1'))
input_SDNAH1_mock = NamedMock(real_name="SDNA Std H1", id='sh1', container=NamedMock(real_name='stds_container_name'),
                              location=(NamedMock(real_name='stds_container_name'), '1:1'))

# generate mock outputs for the 8 standards with 3 replicates each
output1_SDNAA1_mock = NamedMock(real_name="SDNA Std A1-1", container=NamedMock(real_name='OutputContainer1'),
                                location=(NamedMock(real_name="OutputContainer1"), 'A:1'))
output2_SDNAA1_mock = NamedMock(real_name="SDNA Std A1-2", container=NamedMock(real_name='OutputContainer1'),
                                location=(NamedMock(real_name="OutputContainer1"), 'A:2'))
output3_SDNAA1_mock = NamedMock(real_name="SDNA Std A1-3", container=NamedMock(real_name='OutputContainer1'),
                                location=(NamedMock(real_name="OutputContainer1"), 'A:3'))
output1_SDNAB1_mock = NamedMock(real_name="SDNA Std B1-1", container=NamedMock(real_name='OutputContainer1'),
                                location=(NamedMock(real_name="OutputContainer1"), 'B:1'))
output2_SDNAB1_mock = NamedMock(real_name="SDNA Std B1-2", container=NamedMock(real_name='OutputContainer1'),
                                location=(NamedMock(real_name="OutputContainer1"), 'B:2'))
output3_SDNAB1_mock = NamedMock(real_name="SDNA Std B1-3", container=NamedMock(real_name='OutputContainer1'),
                                location=(NamedMock(real_name="OutputContainer1"), 'B:3'))
output1_SDNAC1_mock = NamedMock(real_name="SDNA Std C1-1", container=NamedMock(real_name='OutputContainer1'),
                                location=(NamedMock(real_name="OutputContainer1"), 'C:1'))
output2_SDNAC1_mock = NamedMock(real_name="SDNA Std C1-2", container=NamedMock(real_name='OutputContainer1'),
                                location=(NamedMock(real_name="OutputContainer1"), 'C:2'))
output3_SDNAC1_mock = NamedMock(real_name="SDNA Std C1-3", container=NamedMock(real_name='OutputContainer1'),
                                location=(NamedMock(real_name="OutputContainer1"), 'C:3'))
output1_SDNAD1_mock = NamedMock(real_name="SDNA Std D1-1", container=NamedMock(real_name='OutputContainer1'),
                                location=(NamedMock(real_name="OutputContainer1"), 'D:1'))
output2_SDNAD1_mock = NamedMock(real_name="SDNA Std D1-2", container=NamedMock(real_name='OutputContainer1'),
                                location=(NamedMock(real_name="OutputContainer1"), 'D:2'))
output3_SDNAD1_mock = NamedMock(real_name="SDNA Std D1-3", container=NamedMock(real_name='OutputContainer1'),
                                location=(NamedMock(real_name="OutputContainer1"), 'D:3'))
output1_SDNAE1_mock = NamedMock(real_name="SDNA Std E1-1", container=NamedMock(real_name='OutputContainer1'),
                                location=(NamedMock(real_name="OutputContainer1"), 'E:1'))
output2_SDNAE1_mock = NamedMock(real_name="SDNA Std E1-2", container=NamedMock(real_name='OutputContainer1'),
                                location=(NamedMock(real_name="OutputContainer1"), 'E:2'))
output3_SDNAE1_mock = NamedMock(real_name="SDNA Std E1-3", container=NamedMock(real_name='OutputContainer1'),
                                location=(NamedMock(real_name="OutputContainer1"), 'E:4'))
output1_SDNAF1_mock = NamedMock(real_name="SDNA Std F1-1", container=NamedMock(real_name='OutputContainer1'),
                                location=(NamedMock(real_name="OutputContainer1"), 'F:1'))
output2_SDNAF1_mock = NamedMock(real_name="SDNA Std F1-2", container=NamedMock(real_name='OutputContainer1'),
                                location=(NamedMock(real_name="OutputContainer1"), 'F:2'))
output3_SDNAF1_mock = NamedMock(real_name="SDNA Std F1-3", container=NamedMock(real_name='OutputContainer1'),
                                location=(NamedMock(real_name="OutputContainer1"), 'F:3'))
output1_SDNAG1_mock = NamedMock(real_name="SDNA Std G1-1", container=NamedMock(real_name='OutputContainer1'),
                                location=(NamedMock(real_name="OutputContainer1"), 'G:1'))
output2_SDNAG1_mock = NamedMock(real_name="SDNA Std G1-2", container=NamedMock(real_name='OutputContainer1'),
                                location=(NamedMock(real_name="OutputContainer1"), 'G:2'))
output3_SDNAG1_mock = NamedMock(real_name="SDNA Std G1-3", container=NamedMock(real_name='OutputContainer1'),
                                location=(NamedMock(real_name="OutputContainer1"), 'G:3'))
output1_SDNAH1_mock = NamedMock(real_name="SDNA Std H1-1", container=NamedMock(real_name='OutputContainer1'),
                                location=(NamedMock(real_name="OutputContainer1"), 'H:1'))
output2_SDNAH1_mock = NamedMock(real_name="SDNA Std H1-2", container=NamedMock(real_name='OutputContainer1'),
                                location=(NamedMock(real_name="OutputContainer1"), 'H:2'))
output3_SDNAH1_mock = NamedMock(real_name="SDNA Std H1-3", container=NamedMock(real_name='OutputContainer1'),
                                location=(NamedMock(real_name="OutputContainer1"), 'H:3'))



# checks for number of input containers use all_inputs. Create fake inputs with less than 9 and greate than 9 input plates.

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


def fake_all_inputs2(unique=False, resolve=False):
    """Return a list of 10 mocked artifacts with different container names and locations defined as a tuple."""
    return (
        Mock(id='ai1', type='Analyte', container=NamedMock(real_name='Name1'),
             location=('ContainerVariable1', 'A:1')),
        Mock(id='ai2', type='Analyte', container=(NamedMock(real_name='Name2')),
             location=('ContainerVariable1', 'B:1')),
    )


# checks for numbers of output containers users the all_outputs process function. In the patched processes feed the below outputs dictionaries to the get_all_fake_outputs function
# to generate the required variables in the test


outputs={
    'sa1':[output1_SDNAA1_mock, output2_SDNAA1_mock, output3_SDNAA1_mock],
    'sb1':[output1_SDNAB1_mock, output2_SDNAB1_mock, output3_SDNAB1_mock],
    'sc1':[output1_SDNAC1_mock, output2_SDNAC1_mock, output3_SDNAC1_mock],
    'sd1':[output1_SDNAD1_mock, output2_SDNAD1_mock, output3_SDNAD1_mock],
    'se1':[output1_SDNAE1_mock, output2_SDNAE1_mock, output3_SDNAE1_mock],
    'sf1':[output1_SDNAF1_mock, output2_SDNAF1_mock, output3_SDNAF1_mock],
    'sg1':[output1_SDNAG1_mock, output2_SDNAG1_mock, output3_SDNAG1_mock],
    'sh1':[output1_SDNAH1_mock, output2_SDNAH1_mock,  output3_SDNAH1_mock],
    'ai1':[output1_sample_mock, output2_sample_mock, output3_sample_mock]
}

# three outputs in two output containers
outputs2 = {'ai1': [output1b_sample_mock, output2_sample_mock, output3_sample_mock]}

# four outputs per input
outputs3= {'ai1': [output1_sample_mock, output1_SDNAA1_mock, output2_sample_mock, output3_sample_mock]}


def get_fake_all_outputs(outputs):
    def fake_all_outputs(unique=False, resolve=False):
        return [o for sublist in outputs.values() for o in sublist]

    return fake_all_outputs


def get_fake_outputs_per_input(outputs):
    def fake_outputs_per_input(inputid, ResultFile=True):
        return outputs[inputid]

    return fake_outputs_per_input


class TestGenerateHamiltonSeqQuantPlate(TestEPP):
    def setUp(self):

        step_udfs = {
            'Sample Volume (ul)': '2',
            'Master Mix Volume (ul)': '198',
        }

        dummystep = Mock(reagent_lots= [Mock(id='re1', lot_number='LP9999999-SDNA')])

        self.patched_process1 = patch.object(
            GenerateHamiltonInputSeqQuantPlate,
            'process',
            new_callable=PropertyMock(return_value=Mock(
                all_inputs=fake_all_inputs,
                all_outputs=(get_fake_all_outputs(outputs)),
                udf=step_udfs,
                step=dummystep,
                outputs_per_input=get_fake_outputs_per_input(outputs)


            )
            )
        )

        self.patched_process2 = patch.object(
            GenerateHamiltonInputSeqQuantPlate,
            'process',
            new_callable=PropertyMock(return_value=Mock(
                all_inputs=fake_all_inputs2,
                all_outputs=(get_fake_all_outputs(outputs)),
                udf=step_udfs,
                step=dummystep,
                outputs_per_input=get_fake_outputs_per_input(outputs)
            )
            )
        )

        self.patched_process3 = patch.object(
            GenerateHamiltonInputSeqQuantPlate,
            'process',
            new_callable=PropertyMock(return_value=Mock(
                all_inputs=fake_all_inputs,
                all_outputs=(get_fake_all_outputs(outputs2)),
                udf=step_udfs,
                step=dummystep,
                outputs_per_input=get_fake_outputs_per_input(outputs)
            )
            )
        )

        self.patched_process4 = patch.object(
            GenerateHamiltonInputSeqQuantPlate,
            'process',
            new_callable=PropertyMock(return_value=Mock(
                all_inputs=fake_all_inputs,
                all_outputs=(get_fake_all_outputs(outputs)),
                udf=step_udfs,
                step=dummystep,
                outputs_per_input=get_fake_outputs_per_input(outputs3)
            )
            )
        )

        self.patched_process5 = patch.object(
            GenerateHamiltonInputSeqQuantPlate,
            'process',
            new_callable=PropertyMock(return_value=Mock(
                all_inputs=fake_all_inputs,
                all_outputs=(get_fake_all_outputs(outputs)),
                udf=step_udfs,
                step=Mock(reagent_lots= []),
                outputs_per_input=get_fake_outputs_per_input(outputs)
            )
            )
        )
        self.patched_lims = patch.object(GenerateHamiltonInputSeqQuantPlate, 'lims', new_callable=PropertyMock)

        self.epp = GenerateHamiltonInputSeqQuantPlate(
            self.default_argv + ['-i', 'a_file_location'] + ['-d', self.assets])

    def test_happy_input(self):
        """
        test that files are written under happy path conditions
        i.e. up to 9 input plates, 1 output plate, 3 replicates per input
        """
        with self.patched_process1:
            self.epp._run()

        print(self.stripped_md5('a_file_location-hamilton_input.csv'))
        assert self.stripped_md5('a_file_location-hamilton_input.csv') == '3e3b87e1943f186f31a6ec5c0c6b119a'
        assert self.stripped_md5(self.epp.shared_drive_file_path) == '3e3b87e1943f186f31a6ec5c0c6b119a'

    def test_4_output_artifacts(self):  # the function raises an exception if >3 output artifacts for one input
        with self.patched_process4:
            with pytest.raises(InvalidStepError) as e:
                self.epp._run()
            print(e.value.message)
            assert e.value.message == "3 replicates required for each sample and standard. Did you remember to click 'Apply' when assigning replicates?"


    def test_no_reagent(self):  # the function raises an exception if >3 output artifacts for one input
        with self.patched_process5:
            with pytest.raises(InvalidStepError) as e:
                self.epp._run()
            print(e.value.message)
            assert e.value.message == 'SDNA Plate lot not selected. Please select in "Reagent Lot Tracking" at top of step.'