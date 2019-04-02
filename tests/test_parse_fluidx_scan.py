from os.path import join, dirname, abspath
from unittest.mock import Mock, patch, PropertyMock

import pytest

from EPPs.common import StepEPP
from scripts.parse_fluidx_scan import ParseFluidXScan
from tests.test_common import TestEPP, NamedMock


class TestParseFluidXScan(TestEPP):

    output1=Mock(id=join(dirname(abspath(__file__)), 'assets',
                                                      'fluidx_example_scan.csv'))
    output2=Mock(id=join(dirname(abspath(__file__)), 'assets',
                                                      'fluidx_example_scan_too_many_samples.csv'))

    container=NamedMock(real_name='container1')
    location=[container,'A:1']
    sample1=Mock(udf={'2D Barcode':'-'})
    input1=Mock(location=location, samples=[sample1], container=container)

    patched_process1 = patch.object(
        StepEPP,
        'process',
        new_callable=PropertyMock(return_value=Mock(
            all_inputs=Mock(return_value=[input1])
        )
    ))

    patched_process2 = patch.object(
        StepEPP,
        'process',
        new_callable=PropertyMock(return_value=Mock(
            all_inputs=Mock(return_value=[input1])
        )
    ))

    def setUp(self):

        self.epp = ParseFluidXScan(self.default_argv + ['--fluidx_scan', join(dirname(abspath(__file__)), 'assets',
                                                        'fluidx_example_scan.csv')])

        self.epp2 = ParseFluidXScan(self.default_argv + ['--fluidx_scan', join(dirname(abspath(__file__)), 'assets',
                                                         'fluidx_example_scan_too_many_samples.csv')])

        self.epp3 = ParseFluidXScan(self.default_argv + ['--fluidx_scan', join(dirname(abspath(__file__)), 'assets',
                                                         'fluidx_example_scan_wrong_rack.csv')])

    def test_parse_fluidx_scan(self):
        with self.patched_process1, self.patched_lims as lims:
            self.epp._run()

            assert lims.put_batch.call_count == 1

    def test_parse_fluidx_scan_too_many_samples(self):
        with self.patched_process2, pytest.raises(ValueError) as e:
            self.epp2._run()

        assert str(e.value) == 'The number of samples in the step (1) does not match the number of tubes scanned (2)'

    def test_parse_fluidx_scan_wrong_rack(self):
        with self.patched_process2, pytest.raises(ValueError) as e:
            self.epp3._run()

        assert str(e.value) == 'The scanned rack barcode (container2) does not match the container name in the LIMS (container1)'
