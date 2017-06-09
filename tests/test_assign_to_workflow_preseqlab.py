from EPPs.common import StepEPP
from scripts.assign_workflow_preseqlab import AssignWorkflowPreSeqLab
from tests.test_common import TestEPP, fake_artifact
from unittest.mock import Mock, patch, PropertyMock, MagicMock


def fake_all_inputs(unique=False, resolve=False):
    '''Return a list of mocked artifacts which contain sample which contain artifact ... Simple!'''
    return (
        Mock(samples=[Mock(artifact=fake_artifact(id='a1'), id='s1', udf={"Proceed To SeqLab": True})]),
        Mock(samples=[Mock(artifact=fake_artifact(id='a2'), id='s2', udf={"Proceed To SeqLab": True, "2D Barcode": 'fluidX1'})])
    )


class TestAssignWorkflowPreSeqLab(TestEPP):
    def setUp(self):
        self.patched_process = patch.object(
            AssignWorkflowPreSeqLab,
            'process',
            new_callable=PropertyMock(return_value=Mock(all_inputs=fake_all_inputs))
        )
        self.patched_lims = patch.object(AssignWorkflowPreSeqLab, 'lims', new_callable=PropertyMock)
        self.patched_get_workflow_stage = patch(
            'scripts.assign_workflow_preseqlab.get_workflow_stage',
            return_value=Mock(uri='a_uri')
        )
        self.patch_find_art = patch(
            'scripts.assign_workflow_preseqlab.find_newest_artifact_originating_from',
            return_value=Mock(id='fx2')
        )
        self.epp = AssignWorkflowPreSeqLab(
            'http://server:8080/a_step_uri',
            'a_user',
            'a_password',
            self.log_file
        )

    def test_assign(self):
        with self.patched_get_workflow_stage as pws, self.patched_lims, self.patched_process, self.patch_find_art:
            self.epp._run()

            pws.assert_called_with(self.epp.lims, 'PreSeqLab EG 6.0', 'Sequencing Plate Preparation EG 2.0')
            assert sorted([a.id for a in self.epp.lims.route_artifacts.call_args[0][0]]) == ['a1', 'fx2']
            assert self.epp.lims.route_artifacts.call_args[1] == {'stage_uri': 'a_uri'}

