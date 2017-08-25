from unittest.mock import Mock, patch
from scripts.assign_container_name import AssignContainerName
from tests.test_common import TestEPP, FakeEntity


def fake_output(output_type):
    return Mock(
        output_type=output_type,
        samples=[Mock(project=FakeEntity(name='a_project_'))],
        container=FakeEntity(name='a_container', put=Mock())
    )


class TestAssignContainerName(TestEPP):
    def setUp(self):
        self.epp = AssignContainerName('http://server:8080/a_step_uri', 'a_user', 'a_password', self.log_file)

    def _test_assign(self, get_artifact_calls, expected_container_name):
        fake_outputs = [fake_output('Not an Analyte'), fake_output('Analyte')]
        fake_process = Mock(all_outputs=Mock(return_value=fake_outputs))
        patched_process = patch.object(AssignContainerName, 'process', new=fake_process)
        patched_get_arts = patch.object(
            AssignContainerName, 'lims', new=Mock(get_artifacts=Mock(side_effect=get_artifact_calls))
        )

        with patched_get_arts, patched_process:
            self.epp._run()

        assert fake_outputs[1].container.name == expected_container_name
        fake_outputs[1].container.put.assert_called()

        # should not have touched the non-analyte
        assert fake_outputs[0].container.name == 'a_container'
        fake_outputs[0].container.put.assert_not_called()

    def test_assign_no_arts(self):
        self._test_assign([[]], 'a_project_P001')

    def test_assign_existing_arts(self):
        self._test_assign(['some artifacts', 'some more artifacts', []], 'a_project_P003')

    def test_findAvailableContainer(self):

        with patch.object(self.epp.lims, 'get_artifacts',side_effect=[['something'], ['something'], []]):
            assert self.epp.findAvailableContainer(project='project1', count=1) == 'project1P003'

        with patch.object(self.epp.lims, 'get_artifacts', side_effect=[['a']] * 500 + [[]]):
            assert self.epp.findAvailableContainer(project='project1', count=1) == 'project1P501'
