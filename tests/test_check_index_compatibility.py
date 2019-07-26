from unittest.mock import patch, PropertyMock, Mock

import pytest

from EPPs.common import InvalidStepError
from scripts.check_index_compatibility import CheckIndexCompatibility
from tests.test_common import TestStepEPP, NamedMock


class TestCheckIndexCompatibility(TestStepEPP):
    def setUp(self):
        self.fake_input1 = Mock(reagent_labels=['Name(ATGCATGC-CGTCTGAC)'])
        self.fake_input2 = Mock(reagent_labels=['Name(ATGCATGG-CGTCTGAC)'])
        self.fake_input3 = Mock(reagent_labels=['Name(ATGCATGC-CGTCTGAG)'])
        self.fake_output1 = NamedMock(real_name='Pool1', id='ao1', udf={}, type='Analyte')

        self. process_udfs1 = {'Compatibility Check': 'Single Read', 'Single Read Minimum Hamming Distance': '1',
                         'Dual Read Minimum Hamming Distance': '1'}

        self. process_udfs2 = {'Compatibility Check': 'Dual Read', 'Single Read Minimum Hamming Distance': '1',
                         'Dual Read Minimum Hamming Distance': '1'}

        self.fake_input_output_maps1 = [({'uri': self.fake_input1}, {'limsid': 'ao1'}), ({'uri': self.fake_input2}, {'limsid': 'ao1'})]
        self.fake_input_output_maps2 = [({'uri': self.fake_input1}, {'limsid': 'ao1'}), ({'uri': self.fake_input1}, {'limsid': 'ao1'})]
        self.fake_input_output_maps3 = [({'uri': self.fake_input1}, {'limsid': 'ao1'}), ({'uri': self.fake_input3}, {'limsid': 'ao1'})]
        self.fake_all_outputs = [self.fake_output1]

        self.patched_process = patch.object(
            CheckIndexCompatibility,
            'process',
            new_callable=PropertyMock(return_value=Mock(input_output_maps=self.fake_input_output_maps1,
                                                        all_outputs=Mock(return_value=self.fake_all_outputs),
                                                        udf=self.process_udfs1
                                                        )
                                      )
        )

        self.epp = CheckIndexCompatibility(self.default_argv)

    def test_check_index_compatibility_single_read_happy(self):
        with self.patched_process, self.patched_lims:
            self.epp._run()
            expected_i7_hamming_distance = "1"
            expected_i5_hamming_distance = "0"
            actual_i7_hamming_distance = self.epp.process.all_outputs()[0].udf['Min I7 Hamming Distance']
            actual_i5_hamming_distance = self.epp.process.all_outputs()[0].udf['Min I5 Hamming Distance']

            assert actual_i7_hamming_distance == expected_i7_hamming_distance
            assert actual_i5_hamming_distance == expected_i5_hamming_distance

            assert self.epp.lims.put_batch.call_count == 1

    def test_check_index_compatibility_single_read_unhappy1(self):  # no difference between barcodes
        with self.patched_process as mocked_process, self.patched_lims, pytest.raises(InvalidStepError) as e:
            mocked_process.input_output_maps=self.fake_input_output_maps2
            self.epp._run()

        assert str(e.value) == 'Indexes not compatible within pool Pool1'

    def test_check_index_compatibility_single_read_unhappy2(self):  # difference only between I5
        with self.patched_process as mocked_process, self.patched_lims, pytest.raises(InvalidStepError) as e:
            mocked_process.input_output_maps = self.fake_input_output_maps3
            self.epp._run()

        assert str(e.value) == 'Indexes not compatible within pool Pool1'

    def test_check_index_compatibility_dual_read_happy_i7(self):  # check with difference in i7
        with self.patched_process as mocked_process, self.patched_lims:
            mocked_process.udf=self.process_udfs2
            self.epp._run()

            expected_i7_hamming_distance = "1"
            expected_i5_hamming_distance = "0"
            actual_i7_hamming_distance = self.epp.process.all_outputs()[0].udf['Min I7 Hamming Distance']
            actual_i5_hamming_distance = self.epp.process.all_outputs()[0].udf['Min I5 Hamming Distance']

            assert actual_i7_hamming_distance == expected_i7_hamming_distance
            assert actual_i5_hamming_distance == expected_i5_hamming_distance
            assert self.epp.lims.put_batch.call_count == 1

    def test_check_index_compatibility_dual_read_happy_i5(self):  # check with difference in i5 only
        with self.patched_process as mocked_process, self.patched_lims:
            mocked_process.udf=self.process_udfs2
            mocked_process.input_output_maps = self.fake_input_output_maps3
            self.epp._run()

            expected_i7_hamming_distance = "0"
            expected_i5_hamming_distance = "1"
            actual_i7_hamming_distance = self.epp.process.all_outputs()[0].udf['Min I7 Hamming Distance']
            actual_i5_hamming_distance = self.epp.process.all_outputs()[0].udf['Min I5 Hamming Distance']

            assert actual_i7_hamming_distance == expected_i7_hamming_distance
            assert actual_i5_hamming_distance == expected_i5_hamming_distance
            assert self.epp.lims.put_batch.call_count == 1

    def test_check_index_compatibility_dual_read_unhappy(self):  # no difference between I7 or I5
        with self.patched_process as mocked_process, self.patched_lims, pytest.raises(InvalidStepError) as e:
            mocked_process.udf=self.process_udfs2
            mocked_process.input_output_maps = self.fake_input_output_maps2
            self.epp._run()

        assert str(e.value) == 'Indexes not compatible within pool Pool1'

    def test_calculate_hamming_distance(self): # test a range of different index combinations

        # i7 both  8 bases in length, i5 both 10 bases in length, 1 difference in i7, 2 difference in i5,
        indexes_list = ['ATGCATGT-CGTCTGACTT', 'ATGCATGC-CGTCTGACAA']
        hamming_distance_i7_min, hamming_distance_i5_min = self.epp.calculate_hamming_distances(indexes_list)
        assert hamming_distance_i7_min == 1
        assert hamming_distance_i5_min == 2

        # i7 both 8 bases in length, i5 with 1 10 bases in length and 1 8 bases in length, 3 difference in i7,
        # 0 difference in i5,
        indexes_list = ['ATGCCGGT-CGTCTGAC', 'ATGCATGC-CGTCTGACAA']
        hamming_distance_i7_min, hamming_distance_i5_min = self.epp.calculate_hamming_distances(indexes_list)
        assert hamming_distance_i7_min == 3
        assert hamming_distance_i5_min == 0

        # i7 1 16 bases in length and 1 8 bases in length, i5 with 1 10 bases in length and 1 8 bases in length,
        # 1 difference in i7, 8 difference in i5,
        indexes_list = ['ATGCATGTATGCATGT-ATCACTGA', 'ATGCATGC-CGTCTGACAA']
        hamming_distance_i7_min, hamming_distance_i5_min = self.epp.calculate_hamming_distances(indexes_list)
        assert hamming_distance_i7_min == 1
        assert hamming_distance_i5_min == 8