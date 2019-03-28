from unittest.mock import patch, Mock, PropertyMock

from scripts.generate_manifest import GenerateManifest
from tests.test_common import TestEPP, FakeEntitiesMaker, NamedMock


class TestGenerateManifest(TestEPP):
    udf = {'[Plates]Sample Name': 'A',
           '[Plates]Container Name': 'B',
           '[Plates]Well': 'C',
           '[Plates]Project ID': 'D',
           '[Plates][Sample UDF]Column': 'E',
           '[Plates]Starting Row': 1,
           '[Tubes]Sample Name': 'A',
           '[Tubes]Container Name': 'B',
           '[Tubes]Well': 'C',
           '[Tubes]Project ID Well': 'D1',
           '[Tubes][Sample UDF]Column': 'E',
           '[Tubes]Starting Row': 1,
           '[SGP]Sample Name': 'A',
           '[SGP]Container Name': 'B',
           '[SGP]Well': 'C',
           '[SGP]Project ID Well': 'D1',
           '[SGP][Sample UDF]Column': 'E',
           '[SGP]Starting Row': 1}

    def setUp(self):
        self.epp = GenerateManifest(
            self.default_argv + [
                '--manifest',
                '99-9999'
            ]
        )

    def test_generate_manifest_plate(self):
        fem = FakeEntitiesMaker()
        process_plate = fem.create_a_fake_process(step_udfs=self.udf, project_name='Project1', nb_input=1,
                                                  sample_udfs={'Species': 'Homo sapiens', 'Column': 'value'},
                                                  input_container_type='96 well plate')
        epp = self.epp
        epp.process = process_plate
        with patch('openpyxl.workbook.workbook.Workbook.save') as mocked_save:
            epp._run()
            mocked_save.assert_called_with(
                filename='99-9999-Edinburgh_Genomics_Sample_Submission_Manifest_Project1.xlsx')

    def test_generate_manifest_tube(self):
        fem = FakeEntitiesMaker()
        process_tube = fem.create_a_fake_process(step_udfs=self.udf, project_name='Project1', nb_input=1,
                                                 sample_udfs={'Species': 'Homo sapiens', 'Column': 'value'},
                                                 input_container_type='rack 96 positions')
        epp = self.epp
        epp.process = process_tube
        with patch('openpyxl.workbook.workbook.Workbook.save') as mocked_save:
            self.epp._run()

            mocked_save.assert_called_with(
                filename='99-9999-Edinburgh_Genomics_Sample_Submission_Manifest_Project1.xlsx')

    def test_generate_manifest_sgp(self):
        fem = FakeEntitiesMaker()
        process_sgp = fem.create_a_fake_process(step_udfs=self.udf, project_name='Project1', nb_input=1,
                                                sample_udfs={'Species': 'Homo sapiens', 'Column': 'value'},
                                                input_container_type='SGP rack 96 positions')
        epp = self.epp
        epp.process = process_sgp
        with patch('openpyxl.workbook.workbook.Workbook.save') as mocked_save:
            self.epp._run()

            mocked_save.assert_called_with(
                filename='99-9999-Edinburgh_Genomics_Sample_Submission_Manifest_Project1.xlsx')

    def test_generate_manifest_no_container_type(self):
        self.patch_process = patch.object(
            GenerateManifest,
            'process',
            new_callable=PropertyMock(
                return_value=Mock(
                    all_inputs=Mock(return_value=[
                        Mock(samples=[Mock(project=NamedMock(real_name='Project1'), udf={'Species': 'Homo sapiens'})],
                             container=Mock(type=NamedMock(real_name=None)))])))
        )

        with self.patch_process:
            with self.assertRaises(ValueError):
                self.epp._run()
