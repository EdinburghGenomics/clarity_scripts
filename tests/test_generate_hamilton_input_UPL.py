import hashlib
from unittest.mock import Mock, patch, PropertyMock
from scripts.generate_hamilton_input_UPL import GenerateHamiltonInputUPL
from tests.test_common import TestEPP, NamedMock


def fake_all_inputs1(unique=False, resolve=False):
    """Return a list of 2 mocked artifacts with container names and locations defined as a tuple. The first mocked
    artifact is assigned a name as this is used in one of the error messages during testing"""
    return (
        NamedMock(real_name='artifact_input1', id='ai1', type='Analyte', container=NamedMock(real_name='Name1'),
                  location=('ContainerVariable1', 'A:1')),
        Mock(id='ai2', type='Analyte', container=(NamedMock(real_name='Name2')),
             location=('ContainerVariable1', 'A:1'))
    )


def fake_all_inputs2(unique=False, resolve=False):
    """Return a list of 10 mocked artifacts with container names and locations defined as a tuple."""
    return (
        Mock(id='ai1', type='Analyte', container=NamedMock(real_name='Name1'), location=('ContainerVariable1', 'A:1')),
        Mock(id='ai2', type='Analyte', container=NamedMock(real_name='Name2'), location=('ContainerVariable1', 'A:1')),
        Mock(id='ai3', type='Analyte', container=NamedMock(real_name='Name3'), location=('ContainerVariable1', 'A:1')),
        Mock(id='ai4', type='Analyte', container=NamedMock(real_name='Name4'), location=('ContainerVariable1', 'A:1')),
        Mock(id='ai5', type='Analyte', container=NamedMock(real_name='Name5'), location=('ContainerVariable1', 'A:1')),
        Mock(id='ai6', type='Analyte', container=NamedMock(real_name='Name6'), location=('ContainerVariable1', 'A:1')),
        Mock(id='ai7', type='Analyte', container=NamedMock(real_name='Name7'), location=('ContainerVariable1', 'A:1')),
        Mock(id='ai8', type='Analyte', container=NamedMock(real_name='Name8'), location=('ContainerVariable1', 'A:1')),
        Mock(id='ai9', type='Analyte', container=NamedMock(real_name='Name9'), location=('ContainerVariable1', 'A:1')),
        Mock(id='ai10', type='Analyte', container=NamedMock(real_name='Name10'), location=('ContainerVariable1', 'A:1'))
    )


def fake_outputs_per_input1(inputid, Analyte=False):
    # outputs_per_input is a list of all of the outputs per input obtained from the process by searching with input id
    # the outputs should have the container name and the location defined

    outputs = {
        'ai1': [Mock(id='ao1', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'A:1'))],
        'ai2': [Mock(id='ao1', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'B:1'))],
        'ai3': [Mock(id='bo1', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'C:1'))],
        'ai4': [Mock(id='bo1', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'D:1'))],
        'ai5': [Mock(id='bo1', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'E:1'))],
        'ai6': [Mock(id='bo1', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'F:1'))],
        'ai7': [Mock(id='bo1', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'G:1'))],
        'ai8': [Mock(id='bo1', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'H:1'))],
        'ai9': [Mock(id='bo1', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'A:2'))],
        'ai10': [Mock(id='bo1', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'A:2'))]
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


class TestGenerateHamiltonInputUPL(TestEPP):
    def setUp(self):
        step_udfs = {
            'DNA Volume (uL)': '200',
        }

        self.patched_process1 = patch.object(
            GenerateHamiltonInputUPL,
            'process', new_callable=PropertyMock(return_value=Mock(all_inputs=fake_all_inputs1, udf=step_udfs,
                                                                   outputs_per_input=fake_outputs_per_input1))
        )

        self.patched_process2 = patch.object(
            GenerateHamiltonInputUPL,
            'process', new_callable=PropertyMock(return_value=Mock(all_inputs=fake_all_inputs2, udf=step_udfs,
                                                                   outputs_per_input=fake_outputs_per_input1))
        )

        self.patched_process3 = patch.object(
            GenerateHamiltonInputUPL,
            'process', new_callable=PropertyMock(return_value=Mock(all_inputs=fake_all_inputs1, udf=step_udfs,
                                                                   outputs_per_input=fake_outputs_per_input3))
        )

        self.patched_process4 = patch.object(
            GenerateHamiltonInputUPL,
            'process', new_callable=PropertyMock(return_value=Mock(all_inputs=fake_all_inputs1, udf=step_udfs,
                                                                   outputs_per_input=fake_outputs_per_input2))
        )

        self.epp = GenerateHamiltonInputUPL(self.default_argv + ['-i', 'a_file_location'])

    def test_happy_input(self):  # test that file is written under happy path conditions i.e. <=9 input plates, 1 output
        # per input
        with self.patched_process1:
            self.epp._run()

        def md5(fname):
            hash_md5 = hashlib.md5()
            with open(fname, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()

        assert md5('a_file_location-hamilton_input.csv') == '8bbee080bc09abf9a4773ba14fc766e4'

    def test_10_input_containers(self):  # test that sys exit occurs if >9 input containers
        with self.patched_process2, patch('sys.exit') as mexit:
            self.epp._run()

        mexit.assert_called_once_with(1)

    def test_2_input_containers(self):  # test that sys exit occurs if >1 output containers
        with self.patched_process3, patch('sys.exit') as mexit:
            self.epp._run()

        mexit.assert_called_once_with(1)

    def test_2_output_artifacts(self):  # test that sys exit occurs if >1 output artifacts for one input
        with self.patched_process4, patch('sys.exit') as mexit:
            self.epp._run()

        mexit.assert_called_once_with(1)
