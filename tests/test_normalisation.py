import hashlib
from unittest.mock import Mock, patch, PropertyMock
from scripts.normalisation import CalculateVolumes
from tests.test_common import TestEPP, NamedMock


def fake_all_inputs1(unique=False, resolve=False):
    """Return a list of 2 mocked artifacts as different wells in the same container names and locations defined as a tuple.
    First mocked artifact is given a name as used in error message when checking number of outputs per input"""
    return (
        Mock(id='ai1', type='Analyte', container=NamedMock(real_name='Name1'),
                  udf={'Picogreen Concentration (ng/ul)':55,'CFP_DNA_Volume (uL)':0, 'CFP_RSB_Volume (uL)':0}),
        Mock(id='ai2', type='Analyte', container=(NamedMock(real_name='Name1')),
              udf={'Picogreen Concentration (ng/ul)':30,'CFP_DNA_Volume (uL)':0, 'CFP_RSB_Volume (uL)':0})
    )

class TestNormalisation(TestEPP):
    def setUp(self):
        step_udfs = {
            'KAPA Volume (uL)': '60',
            'KAPA Target DNA Concentration (ng/ul)':'50'
        }

        self.patched_process1 = patch.object(
            CalculateVolumes,
            'process', new_callable=PropertyMock(return_value=Mock(all_inputs=fake_all_inputs1, udf=step_udfs))
        )

        self.patched_lims = patch.object(CalculateVolumes, 'lims', new_callable=PropertyMock)

        self.epp = CalculateVolumes(self.default_argv + ['-n', 'KAPA Volume (uL)'] + ['-t','KAPA Target DNA Concentration (ng/ul)']\
                                            +['-o','Picogreen Concentration (ng/ul)'] + ['-v', 'CFP_DNA_Volume (uL)'] + ['-w','CFP_RSB_Volume (uL)'])

    def test_normalisation(self):
        # per input
        with self.patched_process1:
            self.epp._run()

        assert self.process.all_inputs[0].udf.get['CFP_DNA_Volume (uL'] == 54.5
        assert self.process.all_inputs[1].udf.get['CFP_DNA_Volume (uL'] == 60
        assert self.process.all_inputs[0].udf.get['CFP_RSB_Volume (uL'] == 5.5
        assert self.process.all_inputs[0].udf.get['CFP_RSB_Volume (uL'] == 0

