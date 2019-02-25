from unittest.mock import Mock, patch, PropertyMock

import pytest
from EPPs.common import InvalidStepError

from scripts.generate_hamilton_input_imp_ssqc import GenerateHamiltonInputIMPSSQC
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


def fake_outputs_per_input1(inputid, Analyte=False):
    # outputs_per_input is a list of all of the outputs per input obtained from the process by searching with input id
    # the outputs should have the container name and the location defined

    container1ssqc=NamedMock(real_name='OutputName1-SSQC')
    container2imp=NamedMock(real_name='OutputName2-IMP')

    outputs = {
        'ai1': [Mock(id='ao1', container=container1ssqc, location=(container1ssqc, 'A:1')),
                Mock(id='ao2', container=container2imp, location=(container2imp, 'B:1'))],
        'ai2': [Mock(id='ao3', container=container2imp, location=(container2imp, 'C:1')),
                Mock(id='ao4', container=container1ssqc, location=(container1ssqc, 'D:1'))],

    }
    return outputs[inputid]


def fake_outputs_per_input2(inputid, Analyte=False):
    # outputs_per_input is a list of all of the outputs per input obtained from the process by searching with input id
    # the outputs should have the container name and the location defined. Need to test what happens if two outputs
    # per input present

    outputs = {
        'ai1': [
            Mock(id='bo1', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'A:1'))

        ],
        'ai2': [
            Mock(id='ao1', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'B:1')),
            Mock(id='ao2', container=NamedMock(real_name='OutputName2'), location=('ContainerVariable1', 'C:1'))
        ]
    }
    return outputs[inputid]


outputs1 = {

    'ai1': [Mock(id='ao1', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'A:1')),
            Mock(id='ao3', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'C:1'))],
    'ai2': [Mock(id='ao1', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'B:1'))],
}

outputs2 = {

    'ai1': [Mock(id='ao1', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'A:1'))],
    'ai2': [Mock(id='ao2', container=NamedMock(real_name='OutputName2'), location=('ContainerVariable1', 'B:1'))],
    'ai3': [Mock(id='ao3', container=NamedMock(real_name='OutputName3'), location=('ContainerVariable1', 'B:1'))]

}


def get_fake_all_outputs(outputs):
    def fake_all_outputs(unique=False, resolve=False):
        return [o for sublist in outputs.values() for o in sublist]

    return fake_all_outputs


class TestGenerateHamiltonInputIMP(TestEPP):
    def setUp(self):
        step_udfs = {
            'CFP to IMP Volume (ul)': '50',
            'CFP to SSQC Volume (ul)': '2',
            'RSB to SSQC Volume (ul)': '8',
        }

        dummystep = Mock(reagent_lots=[Mock(id='re1', lot_number='LP9999999-RSB')
                                       ])

        self.patched_process1 = patch.object(
            GenerateHamiltonInputIMPSSQC,
            'process', new_callable=PropertyMock(
                return_value=Mock(
                    all_inputs=fake_all_inputs1, udf=step_udfs,
                    all_outputs=get_fake_all_outputs(outputs1),
                    outputs_per_input=fake_outputs_per_input1,
                    step=dummystep
                ))
        )

        self.patched_process2 = patch.object(
            GenerateHamiltonInputIMPSSQC,
            'process', new_callable=PropertyMock(
                return_value=Mock(
                    all_inputs=fake_all_inputs2, udf=step_udfs,
                    all_outputs=get_fake_all_outputs(outputs1),
                    outputs_per_input=fake_outputs_per_input1,
                    step=dummystep
                ))
        )

        self.patched_process3 = patch.object(
            GenerateHamiltonInputIMPSSQC,
            'process', new_callable=PropertyMock(
                return_value=Mock(
                    all_inputs=fake_all_inputs1, udf=step_udfs,
                    all_outputs=get_fake_all_outputs(outputs2),
                    outputs_per_input=fake_outputs_per_input1,
                    step=dummystep
                ))
        )

        self.patched_process4 = patch.object(
            GenerateHamiltonInputIMPSSQC,
            'process', new_callable=PropertyMock(
                return_value=Mock(
                    all_inputs=fake_all_inputs1, udf=step_udfs,
                    all_outputs=get_fake_all_outputs(outputs1),
                    outputs_per_input=fake_outputs_per_input2,
                    step=dummystep
                ))
        )

        self.patched_lims = patch.object(GenerateHamiltonInputIMPSSQC, 'lims', new_callable=PropertyMock)

        self.epp = GenerateHamiltonInputIMPSSQC(self.default_argv + ['-i', 'an_imp_file_location'] + ['-d', ''])

    def test_happy_input(self):  # test that file is written under happy path conditions i.e. 1 input plate, 1 output
        # per input, 1 output plate
        with self.patched_process1:
            self.epp._run()
            print(self.stripped_md5('an_imp_file_location-hamilton_input.csv'))
            assert self.stripped_md5('an_imp_file_location-hamilton_input.csv') == 'f9253d16ea8bafbed28bbdd2a3f8e323'

    def test_2_input_containers(self):  # test that sys exit occurs if >1 input containers
        with self.patched_process2:
            with pytest.raises(InvalidStepError) as e:
                self.epp._run()
            print(e.value.message)
            assert e.value.message == 'Maximum number of input plates is 1. There are 2 input plates in the step.'

    def test_2_output_containers(self):  # test that sys exit occurs if >1 output containers
        with self.patched_process3:
            with pytest.raises(InvalidStepError) as e:
                self.epp._run()
            print(e.value.message)
            assert e.value.message == 'Maximum number of output plates is 2. There are 3 output plates in the step.'

    def test_2_output_artifacts(self):  # test that sys exit occurs if >1 output artifacts for one input
        with self.patched_process4:
            with pytest.raises(InvalidStepError) as e:
                self.epp._run()
            print(e.value.message)
            assert e.value.message == 'Incorrect number of outputs found for Input1. This step requires two outputs per input.'
