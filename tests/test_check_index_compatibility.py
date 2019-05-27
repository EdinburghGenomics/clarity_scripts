from scripts import check_index_compatibility
from tests.test_common import TestStepEPP


class CheckIndexCompatibility(TestStepEPP):

    def setUp(self):
        self.epp = check_index_compatibility.CheckIndexCompatibility(self.default_argv)

    def test_check_index_compatibility(self):

        expected_i7_hamming_distance = ""
        expected_i5_hamming_distance = ""
        actual_i7_hamming_distance = ""
        actual_i5_hamming_distance = ""

        assert actual_i5_hamming_distance == expected_i5_hamming_distance
