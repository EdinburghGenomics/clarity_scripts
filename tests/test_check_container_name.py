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


def fake_output_containers3(unique=False, resolve=False):
    # generate the fake output containers with defined names
    return (
        NamedMock(real_name='LP1234567-ABC'),
        NamedMock(real_name='LP1234567-AAA')
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

        self.patched_process3 = patch.object(
            CheckContainerName,
            'process', new_callable=PropertyMock(return_value=Mock(output_containers=fake_output_containers3))
        )

        self.epp = CheckContainerName(self.default_argv + ['-x', 'ABC'])
        self.epp2 = CheckContainerName(self.default_argv + ['-x', 'ABC', 'ABB'])

    def test_happy_path_1_containers(
            self):  # test that script completes successfully when suffix and container names match
        with self.patched_process:
            self.epp._run()

    def test_happy_path_2_containers(
            self):  # test that script completes successfully when suffix and container names match
        with self.patched_process2:
            self.epp2._run()

    def test_container_name_not_valid(
            self):  # test error when container present that does not match the name templates
        with self.patched_process3:
            with pytest.raises(InvalidStepError) as e:
                self.epp2._run()

            assert e.value.message == "Container name LP1234567-AAA is not valid for the step. Expected name format is prefix 'LP[0-9]{7}-' with one of the following suffixes: ['ABC', 'ABB']."
