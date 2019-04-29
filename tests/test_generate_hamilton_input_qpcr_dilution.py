from itertools import cycle

from pyclarity_lims.entities import ReagentLot

from scripts.generate_hamilton_input_qpcr_dilution import GenerateHamiltonInputQPCRDilution
from tests.test_common import TestEPP, FakeEntitiesMaker


class TestGenerateHamiltonInputQPCRDilution(TestEPP):

    def setUp(self):
        # argument -d left blank to write file to local directory
        self.epp = GenerateHamiltonInputQPCRDilution(self.default_argv + ['-i', 'a_file_location'] + ['-d', ''])

    def test_generate_hamilton_input_qpcr_dilution(self):
        fem = FakeEntitiesMaker()
        self.epp.lims = fem.lims
        self.epp.process = fem.create_a_fake_process(
            nb_input=2,
            input_artifact_udf={'Adjusted Conc. (nM)': cycle(['36', '35']),
                                'Ave. Conc. (nM)': cycle(['37', '34']),
                                'Original Conc. (nM)': cycle(['38', '33']),
                                '%CV': cycle(['1', '2'])},
            output_artifact_udf={},
            step_udfs={'DCT Volume (ul)': '15',
                       'Threshold Concentration (nM)':'35',
                       'Target Concentration (nM)':'20'},
            output_type='ResultFile'

        )
        self.epp.process.step._reagent_lots.reagent_lots = [
            fem.create_instance(ReagentLot, id='re1', lot_number='LP9999999-RSB')
        ]
        self.epp._validate_step()

        self.epp._run()

        #check that output UDFs are updated as expected
        expected_udf_output1={
            'Adjusted Conc. (nM)': '36',
            'Ave. Conc. (nM)': '37',
            'Original Conc. (nM)': '38',
            '%CV': '1', 'RSB Volume (ul)': '12'
        }

        expected_udf_output2={
            'Adjusted Conc. (nM)': '35',
            'Ave. Conc. (nM)': '34',
            'Original Conc. (nM)': '33',
            '%CV': '2',
            'RSB Volume (ul)': '0'}

        actual_udf_output1=self.epp.process.all_outputs(unique=True)[0].udf
        actual_udf_output2=self.epp.process.all_outputs(unique=True)[1].udf

        assert expected_udf_output1 == actual_udf_output1
        assert expected_udf_output2 == actual_udf_output2


        #check that output files are written correctly
        expected_file_contents = [
            'Input Plate,Input Well,Output Plate,Output Well,Sample Volume,Buffer Barcode,Buffer Volume',
            'input_uri_container_1,A1,input_uri_container_1,A1,15,LP9999999-RSB,12',
            'input_uri_container_1,B1,input_uri_container_1,B1,15,LP9999999-RSB,0']

        expected_file_md5sums = 'b3bd9c97e8745be853f76b99d09aeaef'

        actual_file_lims_contents = self.file_content('a_file_location-hamilton_input.csv')
        actual_file_shareddrive_contents = self.file_content(self.epp.shared_drive_file_path)
        actual_file_lims_md5sums = self.stripped_md5('a_file_location-hamilton_input.csv')
        actual_file_shareddrive_md5sums = self.stripped_md5(self.epp.shared_drive_file_path)


        assert expected_file_contents == actual_file_lims_contents
        assert expected_file_contents == actual_file_shareddrive_contents
        assert actual_file_lims_md5sums == expected_file_md5sums
        assert actual_file_shareddrive_md5sums == expected_file_md5sums
