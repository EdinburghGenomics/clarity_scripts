from unittest.mock import Mock, patch, PropertyMock

from scripts.normalisation import CalculateVolumes
from tests.test_common import TestEPP


def fake_outputs_per_input(inputid, Analyte=False):
    # outputs_per_input is a list of all of the outputs per input obtained from the process by searching with input id
    # the outputs should have the container name and the location defined. Need to test what happens if amongst the
    # outputs for different inputs there are >1 output containers

    outputs = {
        'ai1': [
            Mock(id='bo1', container=NamedMock(real_name='OutputName1'), location=('ContainerVariable1', 'A:1'))],
        'ai2': [
            Mock(id='bo2', container=NamedMock(real_name='OutputName2'), location=('ContainerVariable1', 'A:1'))]
    }
    return outputs[inputid]

class TestNormalisation(TestEPP):



    def setUp(self):
        step_udfs = {
            'KAPA Volume (uL)': 60,
            'KAPA Target DNA Concentration (ng/ul)': 50
        }

        fake_inputs = [
            Mock(id='ai1', type='Analyte',
                 udf={'Picogreen Concentration (ng/ul)': 55})
          ]

        fake_outputs_per_input = [
            Mock(id='bo1', udf={'CFP_DNA_Volume (uL)': 0, 'CFP_RSB_Volume (uL)': 0})]

        self.patched_process1 = patch.object(
            CalculateVolumes,
            'process',
            new_callable=PropertyMock(return_value=Mock(all_inputs=Mock(return_value=fake_inputs), outputs_per_input=Mock(return_value=fake_outputs_per_input), udf=step_udfs)
        ))

        self.patched_lims = patch.object(CalculateVolumes, 'lims', new_callable=PropertyMock)

        self.epp = CalculateVolumes(
            self.default_argv + ['-n', 'KAPA Volume (uL)'] + ['-t', 'KAPA Target DNA Concentration (ng/ul)'] \
            + ['-o', 'Picogreen Concentration (ng/ul)'] + ['-v', 'CFP_DNA_Volume (uL)'] + ['-w', 'CFP_RSB_Volume (uL)'])

    def test_normalisation(self):
        # per input
        with self.patched_process1, self.patched_lims:
            self.epp._run()
            assert self.epp.process.outputs_per_input()[0].udf['CFP_DNA_Volume (uL)'] == 54.5
            assert self.epp.process.outputs_per_input()[0].udf['CFP_RSB_Volume (uL)'] == 5.5

