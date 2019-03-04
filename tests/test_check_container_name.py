import pytest
from EPPs.common import InvalidStepError

from scripts.check_container_name import CheckContainerName
from tests.test_common import TestEPP, FakeEntitiesMaker


class TestCheckContainerName(TestEPP):
    def setUp(self):
        self.epp = CheckContainerName(self.default_argv + ['-x', 'ABC'])
        self.epp2 = CheckContainerName(self.default_argv + ['-x', 'ABC', 'ABB'])

    def test_happy_path_1_containers(self):
        """test that script completes successfully when suffix and container names match"""
        self.epp.process = FakeEntitiesMaker().create_a_fake_process(output_container_name='LP1234567-ABC')
        self.epp._run()


    def test_happy_path_2_containers(self):
        """test that script completes successfully when suffix and container names match"""
        self.epp2.process = FakeEntitiesMaker().create_a_fake_process(
            nb_input=2,
            nb_output_container=2,
            output_container_name=iter(['LP1234567-ABC', 'LP1234567-ABB'])
        )
        self.epp2._run()

    def test_container_name_not_valid(self):
        """test error when container present that does not match the name templates"""
        self.epp2.process = FakeEntitiesMaker().create_a_fake_process(
            nb_input=2,
            nb_output_container=2,
            output_container_name=iter(['LP1234567-ABC', 'LP1234567-AAA'])
        )
        with pytest.raises(InvalidStepError) as e:
            self.epp2._run()

        assert e.value.message == "Container name LP1234567-AAA is not valid for the step. " \
                                  "Expected name format is prefix 'LP[0-9]{7}-' with one of the following suffixes: " \
                                  "['ABC', 'ABB']."
