from scripts.assign_workflow_seqlab_quantstudio import AssignWorkflowSeqLabQuantStudio
from tests.test_common import TestEPP, fake_artifact
from unittest.mock import Mock, patch, PropertyMock, call


def fake_all_outputs(unique=False, resolve=False):
    """Return a list of mocked artifacts which contain samples which contain artifacts... Simple!"""
    return (
        Mock(id='ao1', samples=[Mock(artifact=fake_artifact('a1'), id='s1', udf={'Prep Workflow': 'TruSeq PCR-Free DNA Sample Prep', 'Species': 'Homo sapiens'})]),
        Mock(id='ao2', samples=[Mock(artifact=fake_artifact('a2'), id='s2', udf={'Prep Workflow': 'TruSeq Nano DNA Sample Prep'})]),
        Mock(id='ao3', samples=[Mock(artifact=fake_artifact('a3'), id='s3', udf={'Prep Workflow': 'TruSeq Nano DNA Sample Prep', 'Species': 'Homo sapiens', '2D Barcode': 'fluidX1'})]),
        Mock(id='ao4', samples=[Mock(artifact=fake_artifact('a4'), id='s4', udf={'Prep Workflow': 'KAPA DNA Sample Prep'})])
    )


class TestAssignWorkflowSeqLabQuantStudio(TestEPP):
    def setUp(self):
        self.patched_process = patch.object(
            AssignWorkflowSeqLabQuantStudio,
            'process',
            new_callable=PropertyMock(return_value=Mock(all_outputs=fake_all_outputs))
        )
        self.patched_get_workflow_stage = patch(
            'scripts.assign_workflow_seqlab_quantstudio.get_workflow_stage',
            return_value=Mock(uri='a_uri')
        )
        self.patch_find_art = patch(
            'scripts.assign_workflow_seqlab_quantstudio.find_newest_artifact_originating_from',
            return_value=Mock(id='fx3')
        )
        self.epp = AssignWorkflowSeqLabQuantStudio(self.default_argv)

    def test_assign(self):
        with self.patched_get_workflow_stage as pws, self.patched_lims, self.patched_process, self.patch_find_art:
            self.epp._run()

            pws.assert_has_calls((
                call(self.epp.lims, 'TruSeq PCR-Free DNA Sample Prep', 'Visual QC'),
                call(self.epp.lims, 'TruSeq Nano DNA Sample Prep', 'Visual QC'),
                call(self.epp.lims, 'KAPA Non-Pooling Sample Prep EG 1.0 WFDEV2',
                     'Sequencing Plate Picogreen EG 1.0 ST'),
                call(self.epp.lims, 'QuantStudio EG1.0', 'QuantStudio Plate Preparation EG1.0'),

            ))
            # first routing (pcr free)
            route_args = self.epp.lims.route_artifacts.call_args_list[0]
            assert sorted([a.id for a in route_args[0][0]]) == ['ao1']
            assert self.epp.lims.route_artifacts.call_args[1] == {'stage_uri': 'a_uri'}

            # second routing (nano)
            route_args = self.epp.lims.route_artifacts.call_args_list[1]
            assert sorted([a.id for a in route_args[0][0]]) == ['ao2', 'ao3']

            # third routing (kapa)
            route_args = self.epp.lims.route_artifacts.call_args_list[2]
            assert sorted([a.id for a in route_args[0][0]]) == ['ao4']

            # fourth routing (quantstudio)
            route_args = self.epp.lims.route_artifacts.call_args_list[3]
            assert sorted([a.id for a in route_args[0][0]]) == ['a1', 'fx3']



