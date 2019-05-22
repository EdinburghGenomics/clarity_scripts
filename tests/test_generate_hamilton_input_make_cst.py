from unittest.mock import Mock, PropertyMock, patch

from scripts.generate_hamilton_input_make_cst import GenerateHamiltonInputMakeCST
from tests.test_common import TestEPP, NamedMock


class TestGenerateHamiltonInputMakeCST(TestEPP):
    def setUp(self):
        self.fake_output = Mock(location=[NamedMock(real_name='container3'), 'A:1'])

        fake_input_artifact_list = [Mock(location=[NamedMock(real_name='container1'), 'A:1']),
                                    Mock(location=[NamedMock(real_name='container2'), 'A:1']),
                                    Mock(location=[NamedMock(real_name='container2'), 'B:1'])]

        fake_artifact = Mock(type='Analyte', input_artifact_list=Mock(return_value=fake_input_artifact_list))

        fake_inputs = [fake_artifact]

        step_udfs = {'EPX 1 (uL)': '231', 'EPX 2 (uL)': '33', 'EPX 3 (uL)': '121',
                     'TrisHCL (uL)': '2.5', 'EPX Master Mix (uL)': '35',
                     'PhiX (uL)': '1', 'Library Volume (uL)': '10', 'NaOH (uL)': '2.5', }

        reagent_lots = [
            NamedMock(real_name='EPX1', lot_number='LP9999999-EPX1', reagent_kit=NamedMock(real_name='EPX1')),
            NamedMock(real_name='EPX2', lot_number='LP9999999-EPX2', reagent_kit=NamedMock(real_name='EPX2')),
            NamedMock(real_name='EPX3', lot_number='LP9999999-EPX3', reagent_kit=NamedMock(real_name='EPX3')),
            NamedMock(real_name='PhiX', lot_number='LP9999999-PHIX', reagent_kit=NamedMock(real_name='PhiX')),
            NamedMock(real_name='TrisHCL', lot_number='LP9999999-THCL', reagent_kit=NamedMock(real_name='TrisHCL')),
            NamedMock(real_name='NaOH', lot_number='LP9999999-NAOH', reagent_kit=NamedMock(real_name='NaOH')),
        ]

        self.patched_process1 = patch.object(
            GenerateHamiltonInputMakeCST,
            'process',
            new_callable=PropertyMock(return_value=Mock(all_inputs=Mock(return_value=fake_inputs),
                                                        step=Mock(reagent_lots=reagent_lots),
                                                        outputs_per_input=Mock(return_value=[self.fake_output]),
                                                        udf=step_udfs)
                                      )
        )

        # argument -d left blank to write file to local directory
        self.epp = GenerateHamiltonInputMakeCST(self.default_argv + ['-i', 'a_file_location'] + ['-d', ''])

    def test_generate_hamilton_input_make_cst(self):
        with self.patched_process1:
            self.epp._run()

            expected_file = ['Input Container,Input Well,Library,Output Container,Output Well,EPX1 Barcode,EPX1,'
                             'EPX2 Barcode,EPX2,EPX3 Barcode,EPX3,EPX Master Mix,NaOH Barcode,NaOH,Tris-HCL Barcode,'
                             'Tris-HCL,PhiX Barcode,PhiX',
                             'container1,A1,10,container3,A1,LP9999999-EPX1,231,LP9999999-EPX2,33,LP9999999-EPX3,121,'
                             '35,LP9999999-NAOH,2.5,LP9999999-THCL,2.5,LP9999999-PHIX,1',
                             'container2,A1,10,container3,A1,LP9999999-EPX1,231,LP9999999-EPX2,33,LP9999999-EPX3,121,'
                             '35,LP9999999-NAOH,2.5,LP9999999-THCL,2.5,LP9999999-PHIX,1',
                             'container2,B1,10,container3,A1,LP9999999-EPX1,231,LP9999999-EPX2,33,LP9999999-EPX3,121,'
                             '35,LP9999999-NAOH,2.5,LP9999999-THCL,2.5,LP9999999-PHIX,1']

            expected_md5s = "f750f629036e40ddf948b366322415d7"

            actual_file = self.file_content('a_file_location-hamilton_input.csv')
            actual_lims_md5s = self.stripped_md5('a_file_location-hamilton_input.csv')
            actual_shared_drive_md5s = self.stripped_md5(self.epp.shared_drive_file_path)

            assert actual_file == expected_file
            assert actual_shared_drive_md5s == expected_md5s
            assert actual_lims_md5s == expected_md5s
