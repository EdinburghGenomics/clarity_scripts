from unittest.mock import Mock, patch, PropertyMock

import pytest

from EPPs.common import InvalidStepError
from scripts.normalisation import CalculateVolumes
from tests.test_common import TestEPP, FakeEntitiesMaker


class TestNormalisation(TestEPP):

    def setUp(self):
        fake_artifact1 = Mock()
        fake_artifact2 = Mock()
        fake_artifact3 = Mock()

        fake_sample1 = Mock(artifact=fake_artifact2)

        fake_sample2 = Mock(artifact=fake_artifact2,udf={'Picogreen Concentration (ng/ul)': 75})

        fake_sample3 = Mock(artifact=fake_artifact3, udf={'Another UDF':''})

        fake_artifact1 = Mock(id='ai1', type='Analyte',
                              udf={'Picogreen Concentration (ng/ul)': 55}, samples=[fake_sample1])

        fake_artifact2 = Mock(id='ai3', type='Analyte',
                              udf={'Another UDF': ''}, samples=[fake_sample2])

        fake_artifact3= Mock(id='ai4', type='Analyte',
                              udf={'Another UDF':''}, samples=[fake_sample3])

        step_udfs = {
            'KAPA Volume (uL)': 60,
            'KAPA Target DNA Concentration (ng/ul)': 50
        }

        step_udfs2 = {
            'KAPA Volume (uL)': 60,
        }

        step_udfs3 = {
            'KAPA Target DNA Concentration (ng/ul)': 50
        }

        fake_inputs = [fake_artifact1]

        fake_inputs2 = [fake_artifact2]

        fake_inputs3 = [fake_artifact3]

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

        self.patched_process3 = patch.object(
            CalculateVolumes,
            'process',
            new_callable=PropertyMock(return_value=Mock(all_inputs=Mock(return_value=fake_inputs3),
                                                        outputs_per_input=Mock(return_value=fake_outputs_per_input),
                                                        udf=step_udfs)
                                      ))
        self.patched_process4 = patch.object(
            CalculateVolumes,
            'process',
            new_callable=PropertyMock(return_value=Mock(all_inputs=Mock(return_value=fake_inputs),
                                                        outputs_per_input=Mock(return_value=fake_outputs_per_input),
                                                        udf=step_udfs2)
                                      ))
        self.patched_process5 = patch.object(
            CalculateVolumes,
            'process',
            new_callable=PropertyMock(return_value=Mock(all_inputs=Mock(return_value=fake_inputs),
                                                        outputs_per_input=Mock(return_value=fake_outputs_per_input),
                                                        udf=step_udfs3)
                                      ))


        self.patched_lims = patch.object(CalculateVolumes, 'lims', new_callable=PropertyMock)

        self.epp = CalculateVolumes(
            self.default_argv + ['-n', 'KAPA Volume (uL)'] + ['-t', 'KAPA Target DNA Concentration (ng/ul)'] \
            + ['-o', 'Picogreen Concentration (ng/ul)'] + ['-v', 'CFP_DNA_Volume (uL)'] + ['-w', 'CFP_RSB_Volume (uL)'])

    def test_normalisation_input_derived(self):  # input is derived sample
        # per input
        with self.patched_process1, self.patched_lims:
            self.epp._run()
            assert self.epp.process.outputs_per_input()[0].udf['CFP_DNA_Volume (uL)'] == 54.5
            assert self.epp.process.outputs_per_input()[0].udf['CFP_RSB_Volume (uL)'] == 5.5

    def test_normalisation_input_sample(self):  # input is artifact of the submitted sample

        with self.patched_process2, self.patched_lims:
            self.epp._run()

            assert self.epp.process.outputs_per_input()[0].udf['CFP_DNA_Volume (uL)'] == 40
            assert self.epp.process.outputs_per_input()[0].udf['CFP_RSB_Volume (uL)'] == 20

    def test_normalisation_no_input_conc(self):  # test error message if not input_conc
        # per input
        with self.patched_process3, self.patched_lims, pytest.raises(InvalidStepError) as e:
            self.epp._run()

        assert e.value.message == 'Volume calculation failed due to missing value! Input concentration =  None,' \
                                  ' target concentration = 50 and target volume UDF = 60.'

    def test_normalisation_no_target_conc(self):  # test error message if not input_conc
        # per input
        with self.patched_process4, self.patched_lims, pytest.raises(InvalidStepError) as e:
            self.epp._run()

        assert e.value.message == 'Volume calculation failed due to missing value! Input concentration =  55, target' \
                                  ' concentration = None and target volume UDF = 60.'


    def test_normalisation_no_target_volume(self):  # test error message if not input_conc
        # per input
        with self.patched_process5, self.patched_lims, pytest.raises(InvalidStepError) as e:
            self.epp._run()

        assert e.value.message == 'Volume calculation failed due to missing value! Input concentration =  55,' \
                                  ' target concentration = 50 and target volume UDF = None.'