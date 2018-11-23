from unittest.mock import Mock, patch, PropertyMock

import pytest
from EPPs.common import InvalidStepError

from scripts.check_container_name import CheckContainerName
from tests.test_common import TestEPP, NamedMock


def fake_output_containers(unique=False, resolve=False):
    # generate the fake output containers with defined names
    return (
        NamedMock(real_name='LP1234567-ABC'),
    )


def fake_output_containers2(unique=False, resolve=False):
    # generate the fake output containers with defined names
    return (
        NamedMock(real_name='LP1234567-ABC'),
        NamedMock(real_name='LP1234567-ABB')
    )


class TestCheckContainerName(TestEPP):
    def setUp(self):
        self.patched_process = patch.object(
            CheckContainerName,
            'process', new_callable=PropertyMock(return_value=Mock(output_containers=fake_output_containers))
        )

        self.patched_process2 = patch.object(
            CheckContainerName,
            'process', new_callable=PropertyMock(return_value=Mock(output_containers=fake_output_containers2))
        )
        self.epp = CheckContainerName(self.default_argv + ['-x', 'ABC'])
        self.epp2 = CheckContainerName(self.default_argv + ['-x', 'ABC', 'ABB'])
        self.epp3 = CheckContainerName(self.default_argv + ['-x', 'ABA'])

    def test_happy_path_1_containers(
            self):  # test that script completes successfully when suffix and container names match
        with self.patched_process:
            self.epp._run()

    def test_happy_path_2_containers(
            self):  # test that script completes successfully when suffix and container names match
        with self.patched_process2:
            self.epp2._run()

    def test_suffix_number_incorrect(
            self):  # test that error raised when number of suffixes and containers are different
        with self.patched_process2:
            with pytest.raises(InvalidStepError) as e:
                self.epp3._run()

            assert e.value.message == "The number of plate name suffixes must match the number of output containers. 1 platename suffixes configured for this step and 2 output containers present. The expected suffixes are ['ABA']."

    def test_suffix_incorrect(self):  # test that error raised when suffix and container name do not match
        with self.patched_process:
            with pytest.raises(InvalidStepError) as e:
                self.epp3._run()

            assert e.value.message == "Expected container name format LP[0-9]{7}-ABA does not match container name LP1234567-ABC. Please note that, if more than one container, the order of suffixes ['ABA'] must match the order of containers."
