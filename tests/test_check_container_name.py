from unittest.mock import Mock, patch, PropertyMock
from scripts.check_container_name import CheckContainerName
from tests.test_common import TestEPP, NamedMock


def fake_output_containers(unique=False, resolve=False):
    # generate the fake output containers with defined names
    return (
        NamedMock(real_name='LP1234567-ABC'),
    )


class TestCheckContainerName(TestEPP):
    def setUp(self):
        # generate the fake container names
        self.patched_process = patch.object(
            CheckContainerName,
            'process', new_callable=PropertyMock(return_value=Mock(output_containers=fake_output_containers))
        )

        self.epp = CheckContainerName(self.default_argv + ['-x', 'ABC'])
        self.epp2 = CheckContainerName(self.default_argv + ['-x', 'ABA'])

    def test_suffix_correct(self):  # test that no sys exit occurs when suffix matches container name
        with self.patched_process:
            self.epp._run()

    def test_suffix_incorrect(self):  # test that sys exit occurs when suffix does not match container name
        with self.patched_process, patch('sys.exit') as mexit:
            self.epp2._run()
            mexit.assert_called_once_with(1)
