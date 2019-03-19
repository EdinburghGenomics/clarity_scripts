from unittest.mock import Mock, patch, PropertyMock

from scripts.normalisation import CalculateVolumes
from tests.test_common import TestEPP


class TestNormalisation(TestEPP):

    def setUp(self):
        fake_artifact1 = Mock()
        fake_artifact2 = Mock()

        fake_sample1 = Mock(artifact=fake_artifact2)

        fake_sample2 = Mock(artifact=fake_artifact1)

        fake_artifact1 = Mock(id='ai1', type='Analyte',
                              udf={'Picogreen Concentration (ng/ul)': 55}, samples=[fake_sample1])

        fake_artifact2 = Mock(id='ai3', type='Analyte',
                              udf={'Picogreen Concentration (ng/ul)': 55}, samples=[fake_sample2])

        step_udfs = {
            'KAPA Volume (uL)': 60,
            'KAPA Target DNA Concentration (ng/ul)': 50
        }

        fake_inputs = [fake_artifact1]

        fake_inputs2 = [fake_artifact2]

        fake_outputs_per_input = [
            Mock(id='bo1', udf={'CFP_DNA_Volume (uL)': 0, 'CFP_RSB_Volume (uL)': 0})]

        self.patched_process1 = patch.object(
            CalculateVolumes,
            'process',
            new_callable=PropertyMock(return_value=Mock(all_inputs=Mock(return_value=fake_inputs),
                                                        outputs_per_input=Mock(return_value=fake_outputs_per_input),
                                                        udf=step_udfs)
                                      ))

        self.patched_process2 = patch.object(
            CalculateVolumes,
            'process',
            new_callable=PropertyMock(return_value=Mock(all_inputs=Mock(return_value=fake_inputs2),
                                                        outputs_per_input=Mock(return_value=fake_outputs_per_input),
                                                        udf=step_udfs)
                                      ))

        self.patched_lims = patch.object(CalculateVolumes, 'lims', new_callable=PropertyMock)

        self.epp = CalculateVolumes(
            self.default_argv + ['-n', 'KAPA Volume (uL)'] + ['-t', 'KAPA Target DNA Concentration (ng/ul)'] \
            + ['-o', 'Picogreen Concentration (ng/ul)'] + ['-v', 'CFP_DNA_Volume (uL)'] + ['-w', 'CFP_RSB_Volume (uL)'])

    def test_normalisation_input_derived(self):  # test if input is a derived sample
        # per input
        with self.patched_process1, self.patched_lims:
            self.epp._run()
            assert self.epp.process.outputs_per_input()[0].udf['CFP_DNA_Volume (uL)'] == 54.5
            assert self.epp.process.outputs_per_input()[0].udf['CFP_RSB_Volume (uL)'] == 5.5

    def test_normalisation_input_sample(self):  # test if input is artifact of the submitted sample
        # per input
        with self.patched_process2, self.patched_lims:
            self.epp._run()
            print(self.epp.process.outputs_per_input()[0].udf['CFP_RSB_Volume (uL)'])
            assert self.epp.process.outputs_per_input()[0].udf['CFP_DNA_Volume (uL)'] == 54.5
            assert self.epp.process.outputs_per_input()[0].udf['CFP_RSB_Volume (uL)'] == 5.5
