from os.path import join, dirname, abspath
from unittest.mock import Mock, patch
from tests.test_common import TestEPP, NamedMock,PropertyMock
from scripts.generate_manifest import GenerateManifest


class TestGenerateManifest(TestEPP):
    patch_process = patch.object(
        GenerateManifest,
        'process',
        new_callable=PropertyMock(return_value=
                            Mock(
                                udf={'[Plates]Sample Name':'A',
                                     '[Plates]Container Name':'B',
                                     '[Plates]Well': 'C',
                                     '[Plates]Project ID': 'D',
                                     '[Plates][Sample UDF]Column':'E',
                                     '[Plates]Starting Row': 1,
                                     '[Tubes]Sample Name':'A',
                                     '[Tubes]Container Name': 'B',
                                     '[Tubes]Well': 'C',
                                     '[Tubes]Project ID': 'D',
                                    '[Tubes][Sample UDF]Column':'E',
                                     '[Tubes]Starting Row': 1,
                                     '[SGP]Sample Name':'A',
                                     '[SGP]Container Name': 'B',
                                     '[SGP]Well': 'C',
                                     '[SGP]Project ID': 'D',
                                     '[SGP][Sample UDF]Column':'E',
                                     '[SGP]Starting Row':1},
                                all_inputs=Mock(return_value=[NamedMock(
                                    real_name='Artifact1',
                                    samples=[Mock(project=NamedMock(real_name='Project1'),
                                                  udf={'Species':'Homo sapiens','Column':'value'},
                                                  artifact=NamedMock(real_name='Artifact1',
                                                                     container=NamedMock(real_name='container1'),
                                                                     location=[NamedMock(real_name='container1'),'A:1']))],
                                    container=NamedMock(real_name='container1',type=NamedMock(real_name='96 well plate'))
                                    ,location=[NamedMock(real_name='container1'),'A:1'])]))))


    def setUp(self):
        self.epp = GenerateManifest(
            self.default_argv + [
                '--manifest',
                '99-9999'
            ]
        )

    def test_generate_manifest(self):
        with self.patch_process, patch('openpyxl.workbook.workbook.Workbook.save') as mocked_save:
            self.epp._run()

            mocked_save.assert_called_with(filename='99-9999-Edinburgh_Genomics_Sample_Submission_Manifest_Project1.xlsx')
