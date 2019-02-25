from unittest.mock import Mock, patch, PropertyMock

import pytest
from EPPs.common import InvalidStepError

from scripts.generate_hamilton_input_cfp import GenerateHamiltonInputCFP
from tests.test_common import TestEPP, NamedMock


def fake_all_inputs1(unique=False, resolve=False):
    """Return a list of 2 mocked artifacts as different wells in the same container names and locations defined as a tuple.
    First mocked artifact is given a name as used in error message when checking number of outputs per input"""
    return (
        NamedMock(real_name='Input1', id='ai1', type='Analyte', container=NamedMock(real_name='Name1'),
                  location=('ContainerVariable1', 'A:1')),
        Mock(id='ai2', type='Analyte', container=(NamedMock(real_name='Name1')),
             location=('ContainerVariable1', 'B:1'))
    )


def fake_all_inputs2(unique=False, resolve=False):
    """Return a list of 10 mocked artifacts with different container names and locations defined as a tuple."""
    return (
        Mock(id='ai1', type='Analyte', container=NamedMock(real_name='Name1'),
             location=('ContainerVariable1', 'A:1')),
        Mock(id='ai2', type='Analyte', container=(NamedMock(real_name='Name2')),
             location=('ContainerVariable1', 'B:1')),
        Mock(id='ai3', type='Analyte', container=NamedMock(real_name='Name3'),
             location=('ContainerVariable1', 'A:1')),
        Mock(id='ai4', type='Analyte', container=(NamedMock(real_name='Name4')),
             location=('ContainerVariable1', 'B:1')),
        Mock(id='ai5', type='Analyte', container=NamedMock(real_name='Name5'),
             location=('ContainerVariable1', 'A:1')),
        Mock(id='ai6', type='Analyte', container=(NamedMock(real_name='Name6')),
             location=('ContainerVariable1', 'B:1')),
        Mock(id='ai7', type='Analyte', container=(NamedMock(real_name='Name7')),
             location=('ContainerVariable1', 'B:1')),
        Mock(id='ai8', type='Analyte', container=NamedMock(real_name='Name8'),
             location=('ContainerVariable1', 'A:1')),
        Mock(id='ai9', type='Analyte', container=(NamedMock(real_name='Name9')),
             location=('ContainerVariable1', 'B:1')),
        Mock(id='ai10', type='Analyte', container=NamedMock(real_name='Name10'),
             location=('ContainerVariable1', 'A:1'))

    )


outputs1 = {

    'ai1': [Mock(id='ao1', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'A:1'),
                 udf={'CFP_DNA_Volume (uL)': '50', 'CFP_RSB_Volume (uL)': '10'})],
    'ai2': [Mock(id='ao1', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'B:1'),
                 udf={'CFP_DNA_Volume (uL)': '50', 'CFP_RSB_Volume (uL)': '10'})],
    'ai3': [Mock(id='bo1', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'C:1'),
                 udf={'CFP_DNA_Volume (uL)': '50', 'CFP_RSB_Volume (uL)': '10'})],
    'ai4': [Mock(id='bo1', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'D:1'),
                 udf={'CFP_DNA_Volume (uL)': '50', 'CFP_RSB_Volume (uL)': '10'})],
    'ai5': [Mock(id='bo1', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'E:1'),
                 udf={'CFP_DNA_Volume (uL)': '50', 'CFP_RSB_Volume (uL)': '10'})],
    'ai6': [Mock(id='bo1', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'F:1'),
                 udf={'CFP_DNA_Volume (uL)': '50', 'CFP_RSB_Volume (uL)': '10'})],
    'ai7': [Mock(id='bo1', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'G:1'),
                 udf={'CFP_DNA_Volume (uL)': '50', 'CFP_RSB_Volume (uL)': '10'})],
    'ai8': [Mock(id='bo1', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'H:1'),
                 udf={'CFP_DNA_Volume (uL)': '50', 'CFP_RSB_Volume (uL)': '10'})],
    'ai9': [Mock(id='bo1', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'A:2'),
                 udf={'CFP_DNA_Volume (uL)': '50', 'CFP_RSB_Volume (uL)': '10'})],
    'ai10': [Mock(id='bo1', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'A:2'),
                  udf={'CFP_DNA_Volume (uL)': '50', 'CFP_RSB_Volume (uL)': '10'})]
}

outputs2 = {
    'ai1': [
        Mock(id='bo1', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'A:1'),
             udf={'NTP Library Volume (uL)': '50', 'NTP RSB Volume (uL)': '10'}, type='Analyte'),
    ],
    'ai2': [
        Mock(id='ao1', container=NamedMock(real_name='OutputName2'), location=('ContainerVariable1', 'B:1'),
             udf={'NTP Library Volume (uL)': '50', 'NTP RSB Volume (uL)': '10'}, type='Analyte')
    ]
}

outputs3 = {
    'ai1': [
        Mock(id='bo1', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'A:1'),
             udf={'NTP Library Volume (uL)': '50', 'NTP RSB Volume (uL)': '10'}, type='Analyte'),
        Mock(id='bo2', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'B:1'),
             udf={'NTP Library Volume (uL)': '50', 'NTP RSB Volume (uL)': '10'}, type='Analyte')
    ],
    'ai2': [
        Mock(id='ao1', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'B:1'),
             udf={'NTP Library Volume (uL)': '50', 'NTP RSB Volume (uL)': '10'}, type='Analyte')
    ]
}


def get_fake_all_outputs(outputs):
    def fake_all_outputs(unique=False, resolve=False):
        return [o for sublist in outputs.values() for o in sublist]

    return fake_all_outputs


def get_fake_outputs_per_input(outputs):
    def fake_outputs_per_input(inputid, Analyte=False):
        return outputs[inputid]

    return fake_outputs_per_input


def fake_outputs_per_input2(inputid, Analyte=False):
    # outputs_per_input is a list of all of the outputs per input obtained from the process by searching with input id
    # the outputs should have the container name and the location defined. Need to test what happens if two outputs
    # per input present

    outputs = {
        'ai1': [
            Mock(id='bo1', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'A:1')),
            Mock(id='bo2', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'B:1'))
        ],
        'ai2': [
            Mock(id='ao1', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'B:1'))
        ]
    }
    return outputs[inputid]


def fake_outputs_per_input3(inputid, Analyte=False):
    # outputs_per_input is a list of all of the outputs per input obtained from the process by searching with input id
    # the outputs should have the container name and the location defined. Need to test what happens if amongst the
    # outputs for different inputs there are >1 output containers

    outputs = {
        'ai1': [Mock(id='bo1', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'A:1'))],
        'ai2': [Mock(id='bo2', container=NamedMock(real_name='OutputName2'), location=('ContainerVariable1', 'A:1'))]
    }
    return outputs[inputid]


class TestGenerateHamiltonInputCFP(TestEPP):
    def setUp(self):
        dummystep = Mock(reagent_lots=[Mock(id='re1', lot_number='LP9999999-RSB'),
                                       Mock(id='re2', lot_number='LP9999999-RSA')])

        self.patched_process1 = patch.object(
            GenerateHamiltonInputCFP,
            'process', new_callable=PropertyMock(return_value=Mock(all_inputs=fake_all_inputs1,
                                                                   all_outputs=get_fake_all_outputs(outputs1),
                                                                   outputs_per_input=get_fake_outputs_per_input(
                                                                       outputs1),
                                                                   step=dummystep))
        )

        self.patched_process2 = patch.object(
            GenerateHamiltonInputCFP,
            'process', new_callable=PropertyMock(
                return_value=Mock(all_inputs=fake_all_inputs2,
                                  all_outputs=get_fake_all_outputs(outputs1),
                                  outputs_per_input=get_fake_outputs_per_input(outputs1),
                                  step=dummystep)
            )
        )

        self.patched_process3 = patch.object(
            GenerateHamiltonInputCFP,
            'process', new_callable=PropertyMock(
                return_value=Mock(all_inputs=fake_all_inputs1,
                                  all_outputs=get_fake_all_outputs(outputs2),
                                  outputs_per_input=get_fake_outputs_per_input(outputs2),
                                  step=dummystep)
            )
        )

        self.patched_process4 = patch.object(
            GenerateHamiltonInputCFP,
            'process', new_callable=PropertyMock(
                return_value=Mock(all_inputs=fake_all_inputs1,
                                  all_outputs=get_fake_all_outputs(outputs3),
                                  outputs_per_input=get_fake_outputs_per_input(outputs3),
                                  step=dummystep)
            )
        )

        self.patched_lims = patch.object(GenerateHamiltonInputCFP, 'lims', new_callable=PropertyMock)

        # argument -d left blank to write file to local directory
        self.epp = GenerateHamiltonInputCFP(self.default_argv + ['-i', 'a_file_location'] + ['-d', ''])

    def test_happy_input(self):  # test that file is written under happy path conditions i.e. <=9 input plates, 1 output
        # per input
        with self.patched_process1:
            self.epp._run()

        assert self.stripped_md5('a_file_location-hamilton_input.csv') == '8a9f971359ed6fadd8f1b62f975fe74b'
        assert self.stripped_md5(self.epp.shared_drive_file_path) == '8a9f971359ed6fadd8f1b62f975fe74b'

    def test_10_input_containers(self):  # test that sys exit occurs if >9 input containers
        with self.patched_process2:
            with pytest.raises(InvalidStepError) as e:
                self.epp._run()

            assert e.value.message == 'Maximum number of input plates is 9. There are 10 input plates in the step.'

    def test_2_output_containers(self):  # test that sys exit occurs if >1 output containers
        with self.patched_process3:
            with pytest.raises(InvalidStepError) as e:
                self.epp._run()

            assert e.value.message == 'Maximum number of output plates is 1. There are 2 output plates in the step.'

    def test_2_output_artifacts(self):  # test that sys exit occurs if >1 output artifacts for one input
        with self.patched_process4:
            with pytest.raises(InvalidStepError) as e:
                self.epp._run()

            assert e.value.message == 'Multiple outputs found for an input Input1. This step is not compatible with replicates.'
