from itertools import cycle

from scripts.qpcr_dilution_calculation import QPCRDilutionCalculation
from tests.test_common import TestEPP, FakeEntitiesMaker


class TestQPCRDilutionCalculation(TestEPP):

    def setUp(self):
       self.epp = QPCRDilutionCalculation(self.default_argv)

    def test_qpcr_dilution_calculation(self):
        fem = FakeEntitiesMaker()
        self.epp.lims = fem.lims
        self.epp.process = fem.create_a_fake_process(
            nb_input=2,
            input_artifact_udf={'Adjusted Conc. (nM)': cycle(['36', '35']),
                                'Ave. Conc. (nM)': cycle(['37', '34']),
                                'Original Conc. (nM)': cycle(['38', '33']),
                                '%CV': cycle(['1', '2'])},
            nb_output=2,
            output_type='ResultFile',
            output_artifact_udf={},
            step_udfs={'DCT Volume (ul)': '15',
                       'Threshold Concentration (nM)':'35',
                       'Target Concentration (nM)':'20'}
        )
        self.epp._validate_step()
        self.epp._run()

        expected_rsb_volumes = ['12', '0']
        actual_rsb_volumes = []

        outputs = self.epp.process.all_outputs(unique=True)

        # populate actual rsb volumes list
        for output in outputs:
            if output.type == 'ResultFile':
                actual_rsb_volumes.append(output.udf['RSB Volume (ul)'])


        assert expected_rsb_volumes == actual_rsb_volumes
