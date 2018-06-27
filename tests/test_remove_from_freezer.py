from scripts.remove_from_freezer import UpdateFreezerLocation
from tests.test_common import TestEPP
from unittest.mock import Mock, patch, PropertyMock


class TestUpdateFreezerLocation(TestEPP):
    def setUp(self):
        self.samples = [
            Mock(udf={'Freezer': 'freezer1', 'Shelf': 'upper shelf', 'Box': 'blue one'}),
            Mock(udf={'Freezer': 'freezer2', 'Shelf': 'lower shelf', 'Box': 'red one'})
        ]
        self.patched_samples = patch.object(
            UpdateFreezerLocation,
            'samples',
            new_callable=PropertyMock(return_value=self.samples)
        )
        self.patched_process = patch.object(
            UpdateFreezerLocation,
            'process',
            new_callable=PropertyMock(return_value=Mock(udf={'New Freezer Location': 'In the bin'}))
        )

        self.epp = UpdateFreezerLocation(self.default_argv)

    def test_remove_from_freezer(self):
        with self.patched_samples, self.patched_process:
            self.epp._run()
            # Ensure sample's udfs have been updated
            expected_udf = {'Freezer': 'In the bin', 'Shelf': 'In the bin', 'Box': 'In the bin'}
            for sample in self.samples:
                assert sample.udf == expected_udf
                assert sample.put.call_count == 1
