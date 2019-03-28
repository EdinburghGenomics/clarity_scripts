from unittest.mock import patch, Mock, PropertyMock

import pytest

from scripts.project_udfs_to_step_udfs import ProjectUDFStepUDF
from tests.test_common import TestEPP


class TestProjectUDFToStepUDF(TestEPP):
    step_udfs1 = {'step_udf1': '-', 'step_udf2': '-'}
    step_udfs2 = {'step_udf1': 'step_value1', 'step_udf2': 'step_value2'}

    project_udfs1 = {'project_udf1': 'project_value1', 'project_udf2': 'project_value2'}
    project_udfs2 = {'project_udf1': '-', 'project_udf2': '-'}

    project1 = Mock(udf=project_udfs1)
    project2 = Mock(udf=project_udfs2)

    samples1 = [Mock(project=project1)]
    samples2 = [Mock(project=project2)]

    artifact1 = Mock(samples=samples1)
    artifact2 = Mock(samples=samples2)

    patched_process1 = patch.object(
        ProjectUDFStepUDF,
        'process',
        new_callable=PropertyMock(return_value=Mock(
            udf=step_udfs1,
            all_inputs=Mock(return_value=[artifact1])
        )
        ))

    patched_process2 = patch.object(
        ProjectUDFStepUDF,
        'process',
        new_callable=PropertyMock(return_value=Mock(
            udf=step_udfs2,
            all_inputs=Mock(return_value=[artifact2])
        ))
    )

    def setUp(self):
        super().setUp()
        self.epp1 = ProjectUDFStepUDF(self.default_argv
                                      + ['--project_udfs', 'project_udf1', 'project_udf2']
                                      + ['--step_udfs', 'step_udf1', 'step_udf2']
                                      )

        self.epp2 = ProjectUDFStepUDF(self.default_argv
                                      + ['--project_udfs', 'project_udf1', 'project_udf2']
                                      + ['--step_udfs', 'step_udf1', 'step_udf2']
                                      + ['--reverse']
                                      )
        self.epp3 = ProjectUDFStepUDF(self.default_argv
                                      + ['--project_udfs', 'project_udf1']
                                      + ['--step_udfs', 'step_udf3']
                                      )

        self.epp4 = ProjectUDFStepUDF(self.default_argv
                                      + ['--project_udfs', 'project_udf3']
                                      + ['--step_udfs', 'step_udf1']
                                      )

    def test_project_to_step(self):  # value from project udf to step udf
        with self.patched_process1:
            self.epp1._run()

            assert self.epp2.artifacts[0].samples[0].project.udf['project_udf1'] == 'project_value1'
            assert self.epp2.artifacts[0].samples[0].project.udf['project_udf2'] == 'project_value2'
            assert self.epp2.process.udf['step_udf1'] == 'project_value1'
            assert self.epp2.process.udf['step_udf2'] == 'project_value2'

    def test_step_to_project(self):  # value from project udf to step udf
        with self.patched_process2:
            self.epp2._run()

            assert self.epp2.artifacts[0].samples[0].project.udf['project_udf1'] == 'step_value1'
            assert self.epp2.artifacts[0].samples[0].project.udf['project_udf2'] == 'step_value2'
            assert self.epp2.process.udf['step_udf1'] == 'step_value1'
            assert self.epp2.process.udf['step_udf2'] == 'step_value2'

    def test_step_udf_not_present(self):
        with self.patched_process1, pytest.raises(ValueError) as e:
            self.epp3._run()

        assert str(e.value) == 'Step UDF step_udf3 not present'

    def test_project_udf_not_present(self):
        with self.patched_process1, pytest.raises(ValueError) as e:
            self.epp4._run()

        assert str(e.value) == 'Project UDF project_udf3 not present'
