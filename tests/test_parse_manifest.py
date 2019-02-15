from os.path import join, dirname, abspath
from unittest.mock import Mock, patch

import pytest

from scripts import parse_manifest
from tests.test_common import TestEPP, NamedMock, PropertyMock


class TestParseManifest(TestEPP):

    sample1 = NamedMock(real_name='Key1')
    container = NamedMock(real_name='container1', type=NamedMock(real_name='96 well plate'))
    location=[container, 'A:1']
    artifact1= NamedMock(real_name='Key1',
                samples=[sample1],
                container=container,
                location=location)
    artifact2=  NamedMock(
                    real_name='Key2',
                    samples=[sample1],
                    container=container,
                    location=location
                )
    sample1.project=NamedMock(real_name='Project1')
    sample1.udf={'Species': 'Homo sapiens', 'Column': 'value'}
    sample1.artifact=artifact1


    all_outputs1=[Mock(id=join(dirname(abspath(__file__)), 'assets', 'Manifest_To_Parse.xlsx'))]
    all_outputs2=[Mock(id=join(dirname(abspath(__file__)), 'assets', 'Manifest_To_Parse_too_many.xlsx'))]
    all_outputs3=[Mock(id=join(dirname(abspath(__file__)), 'assets', 'Manifest_To_Parse_too_few.xlsx'))]

    process_udfs={'Plate Sample Name': 'A',
                 '[Plates]Container Name': 'B',
                 '[Plates]Well': 'C',
                 '[Plates]Project ID': 'D',
                 '[Plates][Sample UDF]Column': 'E',
                 'Plate Starting Row': 1,
                 '[Tubes]Sample Name': 'A',
                 '[Tubes]Container Name': 'B',
                 '[Tubes]Well': 'C',
                 '[Tubes]Project ID': 'D',
                 '[Tubes][Sample UDF]Column': 'E',
                 '[Tubes]Starting Row': 1,
                 '[SGP]Sample Name': 'A',
                 '[SGP]Container Name': 'B',
                 '[SGP]Well': 'C',
                 '[SGP]Project ID': 'D',
                 '[SGP][Sample UDF]Column': 'E',
                 '[SGP]Starting Row': 1}

    patch_process1 = patch.object(
        parse_manifest.ParseManifest,
        'process',
        new_callable=PropertyMock(return_value=Mock(
            udf=process_udfs,
            all_inputs=Mock(return_value=[
                artifact1,artifact2]),
            all_outputs=Mock(return_value=all_outputs1
                )
        )
        )
    )

    patch_process2 = patch.object(
        parse_manifest.ParseManifest,
        'process',
        new_callable=PropertyMock(return_value=Mock(
            udf=process_udfs,
            all_inputs=Mock(return_value=[
                artifact1,artifact2]),
            all_outputs=Mock(return_value=all_outputs2
                )
        )
        )
    )

    patch_process3 = patch.object(
        parse_manifest.ParseManifest,
        'process',
        new_callable=PropertyMock(return_value=Mock(
            udf=process_udfs,
            all_inputs=Mock(return_value=[
                artifact1,artifact2]),
            all_outputs=Mock(return_value=all_outputs3
                )
        )
        )
    )


    def setUp(self):

        self.epp = parse_manifest.ParseManifest(self.default_argv + ['--manifest',join(dirname(abspath(__file__)), 'assets', 'Manifest_To_Parse.xlsx') ])
        self.epp2 = parse_manifest.ParseManifest(self.default_argv + ['--manifest',join(dirname(abspath(__file__)), 'assets', 'Manifest_To_Parse_too_many.xlsx') ])
        self.epp3 = parse_manifest.ParseManifest(self.default_argv + ['--manifest',
                                                                      join(dirname(abspath(__file__)), 'assets',
                                                                           'Manifest_To_Parse_too_few.xlsx')])

    def test_parse_manifest_happy_path(self):
        with self.patch_process1, self.patched_lims as lims:
            self.epp._run()

            assert lims.put_batch.call_count == 1

    def test_parse_manifest_sample_too_many(self):
        with self.patch_process2, self.patched_lims:
            with pytest.raises(ValueError) as e:
                self.epp2._run()

            assert str(e.value) == 'Key3 present in manifest but not present in LIMS.'

    def test_parse_manifest_sample_too_few(self):
        with self.patch_process3, self.patched_lims:
            with pytest.raises(ValueError) as e:
                self.epp3._run()

            assert str(e.value)== 'The number of samples in the step does not match the number of samples in the manifest'
