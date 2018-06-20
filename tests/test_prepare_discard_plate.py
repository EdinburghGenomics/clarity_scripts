from EPPs.common import StepEPP
from scripts.prepare_discard_plate import sample_discard_wf_stage_name
from tests.test_common import fake_all_inputs, TestEPP, NamedMock
from unittest.mock import Mock, patch, PropertyMock
from scripts import prepare_discard_plate


class FakeContainer(NamedMock):
    @property
    def placements(self):
        return {
            '1': NamedMock(
                real_name=self.name + ' placement 1',
                samples=[Mock(artifact=Mock(workflow_stages_and_statuses=[(Mock(), 'COMPLETE', sample_discard_wf_stage_name)]))]
            ),
            '2': NamedMock(
                real_name=self.name + ' placement 2',
                samples=[Mock(artifact=Mock(workflow_stages_and_statuses=[(Mock(), 'COMPLETE', sample_discard_wf_stage_name)]))]
            )
        }


def fake_get_artifacts(samplelimsid, type):
    return [Mock(name=type + ' ' + a, container=FakeContainer(real_name='Container ' + a + '-DNA')) for a in samplelimsid]


class TestPrepareDiscardPlate(TestEPP):
    def setUp(self):
        self.epp = prepare_discard_plate.FindPlateToRoute(self.default_argv)
        self.patched_process = patch.object(
            StepEPP,
            'process',
            new_callable=PropertyMock(return_value=Mock(all_inputs=fake_all_inputs))
        )
        self.patched_lims = patch.object(
            StepEPP,
            'lims',
            new_callable=PropertyMock(return_value=Mock(get_artifacts=fake_get_artifacts))
        )

    def test_discard(self):
        patched_stage = patch('scripts.prepare_discard_plate.get_workflow_stage', return_value=Mock(uri='a_uri'))
        patched_log = patch('scripts.prepare_discard_plate.FindPlateToRoute.info')

        exp_log_messages = (
            ('Found Stage %s uri: %s', 'Dispose of Samples EG 1.0 ST', 'a_uri'),
            ('Found %d Samples in the step', 2),
            ('Found %d Analytes (derived samples)', 2),
            ('Found %d containers', 2),
            ('Found %d valid containers to potentially discard', 2),
            ('Found %d others associated with the container but not associated with discarded samples', 4),
            ('Test container %s, with %s artifacts', 'Container s1-DNA', 2),
            (
                'Container %s might route because artifact %s in step_associated_artifacts (%s) or has been discarded before (%s)',
                'Container s1-DNA',
                'Container s1-DNA placement 2',
                False,
                True
            ),
            ('Will route container: %s', 'Container s1-DNA'),
            ('Route %s containers with %s artifacts', 2, 4)
        )

        with patched_log as l, patched_stage as p, self.patched_lims as plims, self.patched_process:
            self.epp._run()
            p.assert_called_with(
                self.epp.lims,
                workflow_name='Sample Disposal EG 1.0 WF',
                stage_name='Dispose of Samples EG 1.0 ST'
            )
            for m in exp_log_messages:
                l.assert_any_call(*m)

            # Has route the artifacts from the containers
            assert plims.route_artifacts.call_count == 1
            assert len(plims.route_artifacts.call_args[0][0]) == 4
            assert plims.route_artifacts.call_args[1] == {'stage_uri': 'a_uri'}


def test_fetch_all_artifacts_for_samples():
    lims = Mock(get_artifacts=Mock(return_value=[1, 2, 3]))
    # 100 samples passed in, window size = 50, so lims should be called twice
    samples = [Mock(id=str(x)) for x in range(100)]
    limsids = [s.id for s in samples]
    assert prepare_discard_plate.fetch_all_artifacts_for_samples(lims, samples) == [1, 2, 3, 1, 2, 3]
    lims.get_artifacts.assert_any_call(samplelimsid=limsids[0:50], type='Analyte')
    lims.get_artifacts.assert_any_call(samplelimsid=limsids[50:100], type='Analyte')


def test_is_valid_container():
    valid_container = NamedMock(real_name='this-GTY')
    assert prepare_discard_plate.is_valid_container(valid_container)
    valid_container = NamedMock(real_name='this-DNA')
    assert prepare_discard_plate.is_valid_container(valid_container)
    invalid_container = NamedMock(real_name='this-QNT')
    assert not prepare_discard_plate.is_valid_container(invalid_container)


def test_has_workflow_stage():
    valid_workflow_stage = ('w', 'COMPLETE', 'a_workflow_step_name')
    invalid_workflow_stage = ('w', 'INCOMPLETE', 'a_workflow_step_name')
    another_invalid_workflow_stage = ('w', 'COMPLETE', 'another_workflow_step_name')

    def artifact(stages):
        a = Mock(workflow_stages_and_statuses=stages)
        return Mock(samples=[Mock(artifact=a)])

    valid_artifact = artifact([invalid_workflow_stage, valid_workflow_stage])
    invalid_artifact = artifact([invalid_workflow_stage, invalid_workflow_stage])
    another_invalid_artifact = artifact([another_invalid_workflow_stage])

    assert prepare_discard_plate.has_workflow_stage(valid_artifact, 'a_workflow_step_name')
    assert not prepare_discard_plate.has_workflow_stage(invalid_artifact, 'a_workflow_step_name')
    assert not prepare_discard_plate.has_workflow_stage(another_invalid_artifact, 'a_workflow_step_name')
