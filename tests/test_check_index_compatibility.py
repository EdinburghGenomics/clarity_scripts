from unittest.mock import patch, PropertyMock, Mock

import pytest

from EPPs.common import InvalidStepError
from scripts.check_index_compatibility import CheckIndexCompatibility
from tests.test_common import TestStepEPP, NamedMock


class TestCheckIndexCompatibility(TestStepEPP):
    def setUp(self):
        fake_input1 = Mock(reagent_labels=['Name(ATGCATGC-CGTCTGAC)'])
        fake_input2 = Mock(reagent_labels=['Name(ATGCATGG-CGTCTGAC)'])
        fake_input3 = Mock(reagent_labels=['Name(ATGCATGC-CGTCTGAG)'])
        fake_output1 = NamedMock(real_name='Pool1', id='ao1', udf={}, type='Analyte')

        process_udfs1 = {'Compatibility Check': 'Single Read', 'Single Read Minimum Hamming Distance': '1',
                         'Dual Read Minimum Hamming Distance': '1'}

        process_udfs2 = {'Compatibility Check': 'Dual Read', 'Single Read Minimum Hamming Distance': '1',
                         'Dual Read Minimum Hamming Distance': '1'}

        fake_input_output_maps1 = [({'uri': fake_input1}, {'limsid': 'ao1'}), ({'uri': fake_input2}, {'limsid': 'ao1'})]
        fake_input_output_maps2 = [({'uri': fake_input1}, {'limsid': 'ao1'}), ({'uri': fake_input1}, {'limsid': 'ao1'})]
        fake_input_output_maps3 = [({'uri': fake_input1}, {'limsid': 'ao1'}), ({'uri': fake_input3}, {'limsid': 'ao1'})]
        fake_all_outputs = [fake_output1]

        self.patched_process1 = patch.object(
            CheckIndexCompatibility,
            'process',
            new_callable=PropertyMock(return_value=Mock(input_output_maps=fake_input_output_maps1,
                                                        all_outputs=Mock(return_value=fake_all_outputs),
                                                        udf=process_udfs1
                                                        )
                                      )
        )

        self.patched_process2 = patch.object(
            CheckIndexCompatibility,
            'process',
            new_callable=PropertyMock(return_value=Mock(input_output_maps=fake_input_output_maps2,
                                                        all_outputs=Mock(return_value=fake_all_outputs),
                                                        udf=process_udfs1
                                                        )
                                      )
        )

        self.patched_process3 = patch.object(
            CheckIndexCompatibility,
            'process',
            new_callable=PropertyMock(return_value=Mock(input_output_maps=fake_input_output_maps3,
                                                        all_outputs=Mock(return_value=fake_all_outputs),
                                                        udf=process_udfs1
                                                        )
                                      )
        )

        self.patched_process4 = patch.object(
            CheckIndexCompatibility,
            'process',
            new_callable=PropertyMock(return_value=Mock(input_output_maps=fake_input_output_maps1,
                                                        all_outputs=Mock(return_value=fake_all_outputs),
                                                        udf=process_udfs2
                                                        )
                                      )
        )

        self.patched_process5 = patch.object(
            CheckIndexCompatibility,
            'process',
            new_callable=PropertyMock(return_value=Mock(input_output_maps=fake_input_output_maps3,
                                                        all_outputs=Mock(return_value=fake_all_outputs),
                                                        udf=process_udfs2
                                                        )
                                      )
        )

        self.patched_process6 = patch.object(
            CheckIndexCompatibility,
            'process',
            new_callable=PropertyMock(return_value=Mock(input_output_maps=fake_input_output_maps2,
                                                        all_outputs=Mock(return_value=fake_all_outputs),
                                                        udf=process_udfs2
                                                        )
                                      )
        )

        self.epp = CheckIndexCompatibility(self.default_argv)

    def test_check_index_compatibility_single_read_happy(self):
        with self.patched_process1, self.patched_lims:
            self.epp.run()

            expected_i7_hamming_distance = "1"
            expected_i5_hamming_distance = "0"
            actual_i7_hamming_distance = self.epp.process.all_outputs()[0].udf['Min I7 Hamming Distance']
            actual_i5_hamming_distance = self.epp.process.all_outputs()[0].udf['Min I5 Hamming Distance']

            assert actual_i7_hamming_distance == expected_i7_hamming_distance
            assert actual_i5_hamming_distance == expected_i5_hamming_distance

            assert self.epp.lims.put_batch.call_count == 1

    def test_check_index_compatibility_single_read_unhappy1(self):  # no difference between barcodes
        with self.patched_process2, self.patched_lims, pytest.raises(InvalidStepError) as e:
            self.epp.run()

        assert str(e.value) == 'Indexes not compatible within pool Pool1'

    def test_check_index_compatibility_single_read_unhappy2(self):  # difference only between I5
        with self.patched_process3, self.patched_lims, pytest.raises(InvalidStepError) as e:
            self.epp.run()

        assert str(e.value) == 'Indexes not compatible within pool Pool1'

    def test_check_index_compatibility_dual_read_happy_i7(self):  # check with difference in i7
        with self.patched_process4, self.patched_lims:
            self.epp.run()

            expected_i7_hamming_distance = "1"
            expected_i5_hamming_distance = "0"
            actual_i7_hamming_distance = self.epp.process.all_outputs()[0].udf['Min I7 Hamming Distance']
            actual_i5_hamming_distance = self.epp.process.all_outputs()[0].udf['Min I5 Hamming Distance']

            assert actual_i7_hamming_distance == expected_i7_hamming_distance
            assert actual_i5_hamming_distance == expected_i5_hamming_distance
            assert self.epp.lims.put_batch.call_count == 1

    def test_check_index_compatibility_dual_read_happy_i5(self):  # check with difference in i5
        with self.patched_process5, self.patched_lims:
            self.epp.run()

            expected_i7_hamming_distance = "0"
            expected_i5_hamming_distance = "1"
            actual_i7_hamming_distance = self.epp.process.all_outputs()[0].udf['Min I7 Hamming Distance']
            actual_i5_hamming_distance = self.epp.process.all_outputs()[0].udf['Min I5 Hamming Distance']

            assert actual_i7_hamming_distance == expected_i7_hamming_distance
            assert actual_i5_hamming_distance == expected_i5_hamming_distance
            assert self.epp.lims.put_batch.call_count == 1

    def test_check_index_compatibility_dual_read_unhappy(self):  # no difference
        with self.patched_process6, self.patched_lims, pytest.raises(InvalidStepError) as e:
            self.epp.run()

        assert str(e.value) == 'Indexes not compatible within pool Pool1'
