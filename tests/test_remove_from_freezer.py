from scripts.remove_from_freezer import UpdateFreezerLocation
from tests.test_common import TestEPP, NamedMock
from unittest.mock import Mock, patch, PropertyMock




class TestUpdateFreezerLocation(TestEPP):
    def setUp(self):

        self.artifacts1 = [
            NamedMock(real_name='Artifact1', id='ai1', udf={'Freezer': 'FreezerTest1', 'Shelf': 'ShelfTest1'}, samples=[NamedMock(artifact=NamedMock(real_name='Artifact1',id='ai1', ), id='s1',
                                                                udf={'Freezer': 'FreezerTest1',
                                                                     'Shelf': 'ShelfTest1'})]),
            NamedMock(real_name='Artifact2', id='ai2',  udf={'Freezer': 'FreezerTest1', 'Shelf': 'ShelfTest1'}, samples=[NamedMock(artifact=NamedMock(real_name='Artifact2',id='ai2', ), id='s2',
                                                                udf={'Freezer': 'FreezerTest1',
                                                                     'Shelf': 'ShelfTest1'})])
        ]

        self.artifacts2 = [
            NamedMock(real_name='Artifact1', id='ai1', udf={'Freezer': 'FreezerTest1', 'Shelf': 'ShelfTest1'}, samples=[NamedMock(artifact=NamedMock(real_name='Artifact1',id='ai2', ), id='s1',
                                                                udf={'Freezer': 'FreezerTest1',
                                                                     'Shelf': 'ShelfTest1'})]),
            NamedMock(real_name='Artifact2', id='ai2',  udf={'Freezer': 'FreezerTest1', 'Shelf': 'ShelfTest1'}, samples=[NamedMock(artifact=NamedMock(real_name='Artifact2',id='ai3', ), id='s2',
                                                                udf={'Freezer': 'FreezerTest1',
                                                                     'Shelf': 'ShelfTest1'})])
        ]


        self.patched_artifacts1 = patch.object(
            UpdateFreezerLocation,
            'artifacts',
            new_callable=PropertyMock(return_value=self.artifacts1))

        self.patched_artifacts2 = patch.object(
            UpdateFreezerLocation,
            'artifacts',
            new_callable=PropertyMock(return_value=self.artifacts2))

        self.patched_process = patch.object(
            UpdateFreezerLocation,
            'process',
            new_callable=PropertyMock(return_value=Mock(udf={'New Freezer Location': 'In the bin'}))
        )

        self.epp = UpdateFreezerLocation(self.default_argv)

    def test_remove_from_freezer1(self):
        with self.patched_artifacts1, self.patched_process:
            self.epp._run()
            # sample UDFs should be updated as the top level artifact matches the sample artifact
            expected_udf = {'Freezer': 'In the bin', 'Shelf': 'In the bin'}
            for artifact in self.artifacts1:
                assert artifact.samples[0].udf == expected_udf
                assert artifact.udf != expected_udf
                assert artifact.samples[0].put.call_count == 1

    def test_remove_from_freezer2(self):
        with self.patched_artifacts2, self.patched_process:
            self.epp._run()
            # sample UDFs should be updated as the top level artifact matches the sample artifact
            expected_udf = {'Freezer': 'In the bin', 'Shelf': 'In the bin'}
            for artifact in self.artifacts2:
                assert artifact.udf == expected_udf
                assert artifact.samples[0].udf != expected_udf
                assert artifact.put.call_count == 1