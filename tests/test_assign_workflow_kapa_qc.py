from itertools import cycle
from unittest.mock import Mock, patch

from scripts.assign_workflow_kapa_qc import AssignWorkflow
from tests.test_common import TestEPP, NamedMock, FakeEntitiesMaker


class TestAssignNextStep(TestEPP):
    def setUp(self):
        self.protostep = NamedMock(real_name='SeqPlatePrepST', uri='http://test.com/config/protocols/1/step/2')

        self.patched_get_workflow_stage = patch(
            'scripts.assign_workflow_kapa_qc.get_workflow_stage',
            return_value=Mock(uri='a_uri')
        )
        protocol = Mock(steps=[self.protostep, Mock(), Mock()])
        self.patched_protocol = patch('scripts.next_step_assignment_kapa_qc.Protocol', return_value=protocol)

        self.epp = AssignWorkflow(self.default_argv + ['-a', 'SeqPlatePrepWF'] + ['-b', 'SeqPlatePrepST']
                                  + ['-c', 'RepeatWF'] + ['-x', 'RepeatST'])

    def test_assign_next_step_seq_plate_prep(self):  # show that samples are assigned to Sequencing Plate Prep
        fem = FakeEntitiesMaker()
        self.epp.lims = fem.lims
        self.epp.process = fem.create_a_fake_process(
            nb_input=2,
            output_artifact_udf={
                'KAPA Next Step': cycle(['KAPA Make Normalised Libraries', 'Sequencing Plate Preparation'])
            },
            next_action=cycle(['nextstep', 'remove'])
        )
        with self.patched_protocol, self.patched_get_workflow_stage as pws:
            self.epp._run()
        pws.assert_called_with(self.epp.lims, "SeqPlatePrepWF", "SeqPlatePrepST")
        fem.lims.route_artifacts.assert_called_with([fem.object_store_per_type.get('Artifact')[3]], stage_uri='a_uri')

    def test_assign_next_step_request_repeats(self):  # show that samples are assigned to request repeats
        fem = FakeEntitiesMaker()
        self.epp.lims = fem.lims
        self.epp.process = fem.create_a_fake_process(
            nb_input=2,
            output_artifact_udf={
                'KAPA Next Step': cycle(['KAPA Make Normalised Libraries', 'Request Repeats'])
            },
            next_action=cycle(['nextstep', 'remove'])
        )
        with self.patched_protocol, self.patched_get_workflow_stage as pws:
            self.epp._run()
        pws.assert_called_with(self.epp.lims, "RepeatWF", "RepeatST")
        fem.lims.route_artifacts.assert_called_with([fem.object_store_per_type.get('Artifact')[3]], stage_uri='a_uri')
