from unittest.mock import Mock, patch
from scripts.assign_container_name import AssignContainerName
from tests.test_common import TestEPP, NamedMock


def fake_output(output_type):
    return Mock(
        output_type=output_type,
        samples=[Mock(project=NamedMock(real_name='a_project_'))],
        container=NamedMock(real_name='a_container')
    )


class TestAssignContainerName(TestEPP):
    def setUp(self):
        self.epp = AssignContainerName(self.default_argv)

    def _test_assign(self, get_containers_calls, expected_container_name):
        fake_outputs = [fake_output('Not an Analyte'), fake_output('Analyte')]
        fake_process = Mock(all_outputs=Mock(return_value=fake_outputs))
        patched_process = patch.object(AssignContainerName, 'process', new=fake_process)
        patched_get_conts = patch.object(self.epp.lims, 'get_containers', side_effect=get_containers_calls)

        with patched_get_conts, patched_process:
            self.epp._run()

        assert fake_outputs[1].container.name == expected_container_name
        fake_outputs[1].container.put.assert_called()

        # should not have touched the non-analytes
        assert fake_outputs[0].container.name == 'a_container'
        fake_outputs[0].container.put.assert_not_called()

    def test_assign_no_arts(self):
        self._test_assign([[]], 'a_project_P001')

    def test_assign_existing_arts(self):
        self._test_assign(['some artifacts', 'some more artifacts', []], 'a_project_P003')

    def test_findAvailableContainer(self):

        with patch.object(self.epp.lims, 'get_containers', side_effect=[['something'], ['something'], []]):
            assert self.epp.find_available_container(project='project1') == 'project1P003'

        with patch.object(self.epp.lims, 'get_containers', side_effect=[['a']] * 500 + [[]]):
            assert self.epp.find_available_container(project='project1', container_type='96 well plate') == 'project1P501'
