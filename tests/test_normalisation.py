from unittest.mock import Mock, patch, PropertyMock

from scripts.normalisation import CalculateVolumes
from tests.test_common import TestEPP


class TestNormalisation(TestEPP):
    def setUp(self):
        step_udfs = {
            'KAPA Volume (uL)': 60,
            'KAPA Target DNA Concentration (ng/ul)': 50
        }

        fake_inputs = (
            Mock(id='ai1', type='Analyte',
                 udf={'Picogreen Concentration (ng/ul)': 55, 'CFP_DNA_Volume (uL)': 5, 'CFP_RSB_Volume (uL)': 0}),
            Mock(id='ai2', type='Analyte',
                 udf={'Picogreen Concentration (ng/ul)': 30, 'CFP_DNA_Volume (uL)': 0, 'CFP_RSB_Volume (uL)': 0})
        )
        self.patched_process1 = patch.object(
            CalculateVolumes,
            'process',
            new_callable=PropertyMock(return_value=Mock(all_inputs=Mock(return_value=fake_inputs), udf=step_udfs))
        )

        self.patched_lims = patch.object(CalculateVolumes, 'lims', new_callable=PropertyMock)

        self.epp = CalculateVolumes(
            self.default_argv + ['-n', 'KAPA Volume (uL)'] + ['-t', 'KAPA Target DNA Concentration (ng/ul)'] \
            + ['-o', 'Picogreen Concentration (ng/ul)'] + ['-v', 'CFP_DNA_Volume (uL)'] + ['-w', 'CFP_RSB_Volume (uL)'])

    def test_normalisation(self):
        # per input
        with self.patched_process1, self.patched_lims:
            self.epp._run()

            assert self.epp.artifacts[0].udf['CFP_DNA_Volume (uL)'] == 54.5
            assert self.epp.artifacts[1].udf['CFP_DNA_Volume (uL)'] == 60
            assert self.epp.artifacts[0].udf['CFP_RSB_Volume (uL)'] == 5.5
            assert self.epp.artifacts[1].udf['CFP_RSB_Volume (uL)'] == 0
