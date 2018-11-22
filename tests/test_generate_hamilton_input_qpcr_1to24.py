from unittest.mock import Mock, patch, PropertyMock

import pytest
from EPPs.common import InvalidStepError

from scripts.generate_hamilton_input_qpcr_1to24 import GenerateHamiltonInputQPCR
from tests.test_common import TestEPP, NamedMock


def fake_all_inputs1(unique=False, resolve=False):
    """Return a list of 1 mocked sample 7 mocked standards artifacts as different wells in the same container names and locations defined as a tuple.
    """
    return (
        NamedMock(real_name='Input1', id='ai1', type='Analyte', container=NamedMock(real_name='InputContainer1'),
                  location=('ContainerVariable1', 'A:1')),
        NamedMock(real_name='Input2', id='ai2', type='Analyte', container=NamedMock(real_name='InputContainer1'),
                  location=('ContainerVariable1', 'B:1')),
        NamedMock(real_name='QSTD A1', id='s1', type='Analyte', container=NamedMock(real_name='Tube'),
                  location=('Tube', '1:1')),
        NamedMock(real_name='QSTD B1', id='s2', type='Analyte', container=NamedMock(real_name='Tube'),
                  location=('Tube', '1:1')),
        NamedMock(real_name='QSTD C1', id='s3', type='Analyte', container=NamedMock(real_name='Tube'),
                  location=('Tube', '1:1')),
        NamedMock(real_name='QSTD D1', id='s4', type='Analyte', container=NamedMock(real_name='Tube'),
                  location=('Tube', '1:1')),
        NamedMock(real_name='QSTD E1', id='s5', type='Analyte', container=NamedMock(real_name='Tube'),
                  location=('Tube', '1:1')),
        NamedMock(real_name='QSTD F1', id='s6', type='Analyte', container=NamedMock(real_name='Tube'),
                  location=('Tube', '1:1')),
        NamedMock(real_name='No Template Control', id='s7', type='Analyte', container=NamedMock(real_name='Tube'),
                  location=('Tube', '1:1')),
    )


def fake_all_inputs2(unique=False, resolve=False):
    """Return a list of 2 mocked artifacts with different container names and locations defined as a tuple."""
    return (
        Mock(id='ai1', type='Analyte', container=NamedMock(real_name='Name1'),
             location=('ContainerVariable1', 'A:1')),
        Mock(id='ai2', type='Analyte', container=(NamedMock(real_name='Name2')),
             location=('ContainerVariable1', 'B:1'))
    )


def fake_outputs_per_input1(inputid, ResultFile=True):
    # outputs_per_input is a list of all of the outputs per input obtained from the process by searching with input id
    # the outputs should have the container name and the location defined

    outputs = {
        'ai1': [Mock(id='ao1', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'A:1'),
                     reagent_labels=['A1_TATAGCCT_ATTACTCG (TATAGCCT_ATTACTCG)']),
                Mock(id='ao1', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'A:1'),
                     reagent_labels=['A1_TATAGCCT_ATTACTCG (TATAGCCT_ATTACTCG)']),
                Mock(id='ao1', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'A:1'),
                     reagent_labels=['A1_TATAGCCT_ATTACTCG (TATAGCCT_ATTACTCG)'])],
        'ai2': [Mock(id='ao4', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'A:1'),
                     reagent_labels=['A1_TATAGCCT_ATTACTCG (TATAGCCT_ATTACTCG)']),
                Mock(id='ao5', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'A:1'),
                     reagent_labels=['A1_TATAGCCT_ATTACTCG (TATAGCCT_ATTACTCG)']),
                Mock(id='ao6', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'A:1'),
                     reagent_labels=['A1_TATAGCCT_ATTACTCG (TATAGCCT_ATTACTCG)'])],
        's1': [Mock(id='ao2', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'B:1')),
               Mock(id='ao2', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'B:1')),
               Mock(id='ao2', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'B:1'))],
        's2': [Mock(id='ao2', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'B:1')),
               Mock(id='ao2', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'B:1')),
               Mock(id='ao2', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'B:1'))],
        's3': [Mock(id='ao2', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'B:1')),
               Mock(id='ao2', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'B:1')),
               Mock(id='ao2', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'B:1'))],
        's4': [Mock(id='ao2', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'B:1')),
               Mock(id='ao2', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'B:1')),
               Mock(id='ao2', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'B:1'))],
        's5': [Mock(id='ao2', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'B:1')),
               Mock(id='ao2', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'B:1')),
               Mock(id='ao2', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'B:1'))],
        's6': [Mock(id='ao2', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'B:1')),
               Mock(id='ao2', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'B:1')),
               Mock(id='ao2', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'B:1'))],
        's7': [Mock(id='ao2', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'B:1')),
               Mock(id='ao2', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'B:1')),
               Mock(id='ao2', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'B:1'))],

    }
    return outputs[inputid]


def fake_outputs_per_input2(inputid, ResultFile=True):
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


outputs1 = {

    'ai1': [Mock(id='ao1', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'A:1'))],
    'ai2': [Mock(id='ao2', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'B:1'))],
}

outputs2 = {

    'ai1': [Mock(id='ao1', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'A:1'))],
    'ai2': [Mock(id='ao2', container=NamedMock(real_name='OutputName2'), location=('ContainerVariable1', 'B:1'))],

}


def get_fake_all_outputs(outputs):
    def fake_all_outputs(unique=False, resolve=False):
        return [o for sublist in outputs.values() for o in sublist]

    return fake_all_outputs


def fake_reagent_lots():
    return (
        Mock(id='re1', lot_number='LP9999999-QSTD'),
        Mock(id='re2', lot_number='LP9999999-QMX')
    )


class TestGenerateHamiltonInputQPCR(TestEPP):
    def setUp(self):
        step_udfs = {
            'DIL1 Plate Barcode': 'LP9999999-DIL1',
            'DIL2 Plate Barcode': 'LP9999999-DIL2'
        }

        step_udfs2 = {
            'DIL1 Plate Barcode': 'LP9999999-DOT1',
            'DIL2 Plate Barcode': 'LP9999999-DIL2'
        }

        step_udfs3 = {
            'DIL1 Plate Barcode': 'LP9999999-DIL1',
            'DIL2 Plate Barcode': 'LP9999999-DOT2'
        }

        self.patched_process1 = patch.object(
            GenerateHamiltonInputQPCR,
            'process', new_callable=PropertyMock(
                return_value=Mock(
                    all_inputs=fake_all_inputs1, udf=step_udfs,
                    all_outputs=get_fake_all_outputs(outputs1),
                    outputs_per_input=fake_outputs_per_input1,
                    step=Mock(reagent_lots=fake_reagent_lots())
                ))
        )

        self.patched_process2 = patch.object(
            GenerateHamiltonInputQPCR,
            'process', new_callable=PropertyMock(
                return_value=Mock(
                    all_inputs=fake_all_inputs2, udf=step_udfs,
                    all_outputs=get_fake_all_outputs(outputs1),
                    outputs_per_input=fake_outputs_per_input1,
                    step=Mock(reagent_lots=fake_reagent_lots())
                ))
        )

        self.patched_process3 = patch.object(
            GenerateHamiltonInputQPCR,
            'process', new_callable=PropertyMock(
                return_value=Mock(
                    all_inputs=fake_all_inputs1, udf=step_udfs,
                    all_outputs=get_fake_all_outputs(outputs2),
                    outputs_per_input=fake_outputs_per_input1,
                    step=Mock(reagent_lots=fake_reagent_lots())
                ))
        )

        self.patched_process4 = patch.object(
            GenerateHamiltonInputQPCR,
            'process', new_callable=PropertyMock(
                return_value=Mock(
                    all_inputs=fake_all_inputs1, udf=step_udfs,
                    all_outputs=get_fake_all_outputs(outputs1),
                    outputs_per_input=fake_outputs_per_input2,
                    step=Mock(reagent_lots=fake_reagent_lots())
                ))
        )

        self.patched_process5 = patch.object(
            GenerateHamiltonInputQPCR,
            'process', new_callable=PropertyMock(
                return_value=Mock(
                    all_inputs=fake_all_inputs1, udf=step_udfs2,
                    all_outputs=get_fake_all_outputs(outputs1),
                    outputs_per_input=fake_outputs_per_input1,
                    step=Mock(reagent_lots=fake_reagent_lots())
                ))
        )

        self.patched_process6 = patch.object(
            GenerateHamiltonInputQPCR,
            'process', new_callable=PropertyMock(
                return_value=Mock(
                    all_inputs=fake_all_inputs1, udf=step_udfs3,
                    all_outputs=get_fake_all_outputs(outputs1),
                    outputs_per_input=fake_outputs_per_input1,
                    step=Mock(reagent_lots=fake_reagent_lots())
                ))
        )

        self.patched_lims = patch.object(GenerateHamiltonInputQPCR, 'lims', new_callable=PropertyMock)

        self.epp = GenerateHamiltonInputQPCR(self.default_argv + ['-i', 'a_file_location'] + ['-d', self.assets])

    def test_happy_input(self):  # test that file is written under happy path conditions i.e. 1 input plate, 1 output
        # per input, 1 output plate
        with self.patched_process1:
            self.epp._run()

            assert self.stripped_md5('assets/MAKE_QPCR-1_TO_24_INPUT.csv') == 'd0d07df6d608cc62f50bf4051779a7a5'
            assert self.stripped_md5(self.epp.shared_drive_file_path) == 'd0d07df6d608cc62f50bf4051779a7a5'

    def test_2_input_containers(self):  # test that error occurs if >1 input containers
        with self.patched_process2:
            with pytest.raises(InvalidStepError) as e:
                self.epp._run()

            assert e.value.message == 'Maximum number of input plates is 1. There are 2 input plates in the step.'

    def test_2_output_containers(self):  # test that error occurs if >1 output containers
        with self.patched_process3:
            with pytest.raises(InvalidStepError) as e:
                self.epp._run()
            print(e.value.message)
            assert e.value.message == 'Maximum number of output plates is 1. There are 2 output plates in the step.'

    def test_2_output_artifacts(self):  # test that error occurs if not 3 output artifacts for one input
        with self.patched_process4:
            with pytest.raises(InvalidStepError) as e:
                self.epp._run()
            print(e.value.message)
            assert e.value.message == '2 outputs found for an input Input1. 3 replicates required.'

    def test_not_DIL1(self):  # test that sys exit occurs if DIL1 barcode does not have correct format
        with self.patched_process5:
            with pytest.raises(InvalidStepError) as e:
                self.epp._run()
            print(e.value.message)
            assert e.value.message == 'LP9999999-DOT1 is not a valid DIL1 container name. Container names must match LP[0-9]{7}-DIL1'

    def test_not_DIL2(self):  # test that sys exit occurs if DIL2 barcode does not have correct format
        with self.patched_process6:
            with pytest.raises(InvalidStepError) as e:
                self.epp._run()
            print(e.value.message)
            assert e.value.message == 'LP9999999-DOT2 is not a valid DIL2 container name. Container names must match LP[0-9]{7}-DIL2'
