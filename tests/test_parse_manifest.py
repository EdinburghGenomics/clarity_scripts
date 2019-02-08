from os.path import join, dirname, abspath
from unittest.mock import Mock, patch

from io import BytesIO

from tests.test_common import TestEPP, NamedMock,PropertyMock
from scripts.parse_manifest import ParseManifest


class TestParseManifest(TestEPP):
    container=NamedMock(real_name='container1', type=NamedMock(real_name='96 well plate'))

    patch_process = patch.object(
        ParseManifest,
        'process',
        new_callable=PropertyMock(return_value=
                            Mock(
                                udf={'Plate Sample Name':'A',
                                     '[Plates]Container Name':'B',
                                     '[Plates]Well': 'C',
                                     '[Plates]Project ID': 'D',
                                     '[Plates][Sample UDF]Column':'E',
                                     'Plate Starting Row': 1,
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
                                    real_name='Key1',
                                    samples=[NamedMock(real_name='Key1',project=NamedMock(real_name='Project1'),
                                                  udf={'Species':'Homo sapiens','Column':'value'},
                                                  artifact=NamedMock(real_name='Artifact1',
                                                                     container=container,
                                                                     location=[container,'A:1']))],
                                    container=container
                                    ,location=[container,'A:1']),
                                    NamedMock(
                                        real_name='Key2',
                                        samples=[NamedMock(real_name='Key1', project=NamedMock(real_name='Project1'),
                                                           udf={'Species': 'Homo sapiens', 'Column': 'value'},
                                                           artifact=NamedMock(real_name='Artifact1',
                                                                              container=container,
                                                                              location=[
                                                                                  NamedMock(real_name='container1'),
                                                                                  'A:1']))],
                                        container=container
                                        , location=[container, 'A:1'])
                                ]),
                                all_outputs=Mock(return_value=[Mock(id=join(dirname(abspath(__file__)), 'assets', 'Manifest_To_Parse.xlsx'))]
                                                 ))))


    def setUp(self):
        self.epp = ParseManifest(
            self.default_argv + [
                '--manifest',
                join(dirname(abspath(__file__)), 'assets', 'Manifest_To_Parse.xlsx')
            ]
        )

    #join(dirname(abspath(__file__)), 'assets', 'Manifest_To_Parse.xlsx')

    def test_parse_manifest(self):
        with self.patch_process, self.patched_lims:
            self.epp._run()
            #mocked_put_batchput_batch.assert_called_with(filename='99-9999-Edinburgh_Genomics_Sample_Submission_Manifest_Project1.xlsx')

