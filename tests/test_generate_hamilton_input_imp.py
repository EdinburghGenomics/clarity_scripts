from unittest.mock import Mock, patch, PropertyMock

from scripts.generate_hamilton_input_imp import GenerateHamiltonInputIMP
from tests.test_common import TestEPP, NamedMock


def fake_all_inputs1(unique=False, resolve=False):
    """Return a list of 2 mocked artifacts as different wells in the same container names and locations defined as a tuple.
    First mocked artifact is given a name as used in error message when checking number of outputs per input"""
    return (
       NamedMock(real_name='Input1', id='ai1', type='Analyte', container=NamedMock(real_name='Name1'),
                  location=('ContainerVariable1', 'A:1'), udf={'CFP_DNA_Volume (uL)':'50', 'CFP_RSB_Volume (uL)':'10'}),
        Mock(id='ai2', type='Analyte', container=(NamedMock(real_name='Name1')),
             location=('ContainerVariable1', 'B:1'), udf={'CFP_DNA_Volume (uL)':'50', 'CFP_RSB_Volume (uL)':'10'})
    )


def fake_all_inputs2(unique=False, resolve=False):
    """Return a list of 2 mocked artifacts with different container names and locations defined as a tuple."""
    return (
        Mock(id='ai1', type='Analyte', container=NamedMock(real_name='Name1'),
                  location=('ContainerVariable1', 'A:1'), udf={'CFP_DNA_Volume (uL)':'50', 'CFP_RSB_Volume (uL)':'10'}),
        Mock(id='ai2', type='Analyte', container=(NamedMock(real_name='Name2')),
             location=('ContainerVariable1', 'B:1'), udf={'CFP_DNA_Volume (uL)':'50', 'CFP_RSB_Volume (uL)':'10'})
    )


def fake_outputs_per_input1(inputid, Analyte=False):
    # outputs_per_input is a list of all of the outputs per input obtained from the process by searching with input id
    # the outputs should have the container name and the location defined

    outputs = {
        'ai1': [Mock(id='ao1', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'A:1'))],
        'ai2': [Mock(id='ao2', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'B:1'))],

    }
    return outputs[inputid]


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

class TestGenerateHamiltonInputIMP(TestEPP):
    def setUp(self):
        step_udfs = {
            'CFP Volume (ul)': '50',
        }

        dummystep = Mock(reagent_lots= [Mock(id='re1', lot_number='LP9999999-RSB'),
        Mock(id='re2',lot_number='LP9999999-RSA')])


        self.patched_process1 = patch.object(
            GenerateHamiltonInputIMP,
            'process', new_callable=PropertyMock(return_value=Mock(all_inputs=fake_all_inputs1, udf=step_udfs,
                                                                   outputs_per_input=fake_outputs_per_input1, step=dummystep))
        )

        self.patched_process2 = patch.object(
            GenerateHamiltonInputIMP,
            'process', new_callable=PropertyMock(return_value=Mock(all_inputs=fake_all_inputs2, udf=step_udfs,
                                                                   outputs_per_input=fake_outputs_per_input1, step=dummystep))
        )

        self.patched_process3 = patch.object(
            GenerateHamiltonInputIMP,
            'process', new_callable=PropertyMock(return_value=Mock(all_inputs=fake_all_inputs1, udf=step_udfs,
                                                                   outputs_per_input=fake_outputs_per_input3, step=dummystep))
        )

        self.patched_process4 = patch.object(
            GenerateHamiltonInputIMP,
            'process', new_callable=PropertyMock(return_value=Mock(all_inputs=fake_all_inputs1, udf=step_udfs,
                                                                   outputs_per_input=fake_outputs_per_input2, step=dummystep))
        )

        self.patched_lims = patch.object(GenerateHamiltonInputIMP, 'lims', new_callable=PropertyMock)

        self.epp = GenerateHamiltonInputIMP(self.default_argv + ['-i', 'an_imp_file_location'] + ['-d','test'])

    def test_happy_input(self):  # test that file is written under happy path conditions i.e. 1 input plate, 1 output
        # per input, 1 output plate
        with self.patched_process1:
            self.epp._run()

            assert self.stripped_md5('an_imp_file_location-hamilton_input.csv') == 'f59a2eba0cd5729a59f00fb892806cf9'

    def test_2_input_containers(self):  # test that sys exit occurs if >1 input containers
        with self.patched_process2, patch('sys.exit') as mexit:
            self.epp._run()

        mexit.assert_called_once_with(1)

    def test_2_output_containers(self):  # test that sys exit occurs if >1 output containers
        with self.patched_process3, patch('sys.exit') as mexit:
            self.epp._run()

        mexit.assert_called_once_with(1)

    def test_2_output_artifacts(self):  # test that sys exit occurs if >1 output artifacts for one input
        with self.patched_process4, patch('sys.exit') as mexit:
            self.epp._run()

        mexit.assert_called_once_with(1)