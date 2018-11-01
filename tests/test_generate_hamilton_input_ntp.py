from unittest.mock import Mock, patch, PropertyMock

import pytest

from EPPs.common import InvalidStepError
from scripts.generate_hamilton_input_ntp import GenerateHamiltonInputNTP
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
    """Return a list of 2 mocked artifacts with different container names and locations defined as a tuple."""
    return (
        Mock(id='ai1', type='Analyte', container=NamedMock(real_name='Name1'),
             location=('ContainerVariable1', 'A:1')),
        Mock(id='ai2', type='Analyte', container=(NamedMock(real_name='Name2')),
             location=('ContainerVariable1', 'B:1'))
    )


# outputs_per_input is a list of all of the outputs per input obtained from the process by searching with input id
# the outputs should have the container name and the location defined.
outputs1 = {
    'ai1': [Mock(id='ao1', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'A:1'),
                 udf={'NTP Library Volume (uL)': '50', 'NTP RSB Volume (uL)': '10'}, type='Analyte')],
    'ai2': [Mock(id='ao1', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'B:1'),
                 udf={'NTP Library Volume (uL)': '40', 'NTP RSB Volume (uL)': '20'}, type='Analyte')],
}

outputs2 = {
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


outputs3 = {
    'ai1': [Mock(id='bo1', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'A:1'),
                 udf={'NTP Library Volume (uL)': '50', 'NTP RSB Volume (uL)': '10'}, type='Analyte')],
    'ai2': [Mock(id='bo2', container=NamedMock(real_name='OutputName2'), location=('ContainerVariable1', 'A:1'),
                 udf={'NTP Library Volume (uL)': '50', 'NTP RSB Volume (uL)': '10'}, type='Analyte')]
}


def get_fake_all_outputs(outputs):
    def fake_all_outputs(unique=False, resolve=False):
        return [o for sublist in outputs.values() for o in sublist]
    return fake_all_outputs


def get_fake_outputs_per_input(outputs):
    def fake_outputs_per_input(inputid, Analyte=False):
        return outputs[inputid]
    return fake_outputs_per_input


def fake_reagent_lots():
    return
    (
        [Mock(id='re1', lot_number='LP9999999-RSB'),
         Mock(id='re2', lot_number='LP9999999-RSA')]
    )


class TestGenerateHamiltonInputNTP(TestEPP):
    def setUp(self):
        dummystep = Mock(reagent_lots=[Mock(id='re1', lot_number='LP9999999-RSB'),
                                       Mock(id='re2', lot_number='LP9999999-RSA')])

        self.patched_process1 = patch.object(
            GenerateHamiltonInputNTP,
            'process', new_callable=PropertyMock(
                return_value=Mock(all_inputs=fake_all_inputs1,
                                  all_outputs=get_fake_all_outputs(outputs1),
                                  outputs_per_input=get_fake_outputs_per_input(outputs1),
                                  step=dummystep)
            )
        )

        self.patched_process2 = patch.object(
            GenerateHamiltonInputNTP,
            'process', new_callable=PropertyMock(
                return_value=Mock(all_inputs=fake_all_inputs2,
                                  all_outputs=get_fake_all_outputs(outputs1),
                                  outputs_per_input=get_fake_outputs_per_input(outputs1),
                                  step=dummystep)
            )
        )

        self.patched_process3 = patch.object(
            GenerateHamiltonInputNTP,
            'process', new_callable=PropertyMock(
                return_value=Mock(all_inputs=fake_all_inputs1,
                                  all_outputs=get_fake_all_outputs(outputs3),
                                  outputs_per_input=get_fake_outputs_per_input(outputs3),
                                  step=dummystep)
            )
        )

        self.patched_process4 = patch.object(
            GenerateHamiltonInputNTP,
            'process', new_callable=PropertyMock(
                return_value=Mock(all_inputs=fake_all_inputs1,
                                  all_outputs=get_fake_all_outputs(outputs2),
                                  outputs_per_input=get_fake_outputs_per_input(outputs2),
                                  step=dummystep))
        )

        self.patched_lims = patch.object(GenerateHamiltonInputNTP, 'lims', new_callable=PropertyMock)

        self.epp = GenerateHamiltonInputNTP(self.default_argv + ['-i', 'a_file_location'] + ['-d', self.assets])

    def test_happy_input(self):
        """
        test that files are written under happy path conditions
        i.e. 1 input plate, 1 output plate, 1 output per input
        """
        with self.patched_process1:
            self.epp._run()

        assert self.stripped_md5('a_file_location-hamilton_input.csv') == '9141fb8835df521d4475907a65f9af66'
        assert self.stripped_md5(self.epp.shared_drive_file_path) == '9141fb8835df521d4475907a65f9af66'

    def test_2_input_containers(self):  # the function raises an exception if >1 input containers
        with self.patched_process2:
            with pytest.raises(InvalidStepError) as e:
                self.epp._run()
            assert e.value.message == 'Maximum number of input plates is 1. There are 2 input plates in the step.'

    def test_2_output_containers(self):  # the function raises an exception if >1 output containers
        with self.patched_process3:
            with pytest.raises(InvalidStepError) as e:
                self.epp._run()
            assert e.value.message == 'Maximum number of output plates is 1. There are 2 output plates in the step.'

    def test_2_output_artifacts(self):  # the function raises an exception if >1 output artifacts for one input
        with self.patched_process4:
            with pytest.raises(InvalidStepError) as e:
                self.epp._run()
                assert e.value.message == 'Multiple outputs found for an input ai1. ' \
                                    'This step is not compatible with replicates.'
