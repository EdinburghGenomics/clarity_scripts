from tests.test_common import fake_all_inputs, TestEPP, FakeEntity
from unittest.mock import Mock, patch
from EPPs import prepare_discard_plate


class FakeContainer(FakeEntity):
    type = Mock()

    def __init__(self, name):
        super().__init__(name)
        self.placements = {
            '1': FakeEntity(
                name=name + ' placement 1',
                samples=[Mock(artifact=Mock(workflow_stages_and_statuses=[(Mock(), Mock(), Mock())]))]
            ),
            '2': FakeEntity(
                name=name + ' placement 2',
                samples=[Mock(artifact=Mock(workflow_stages_and_statuses=[(Mock(), Mock(), Mock())]))]
            )
        }


def fake_artifacts(samplelimsid, type):
    return [Mock(name=type + ' ' + a, container=FakeContainer(name='Container ' + a)) for a in samplelimsid]


class TestPrepareDiscardPlate(TestEPP):
    def setUp(self):
        self.epp = prepare_discard_plate.FindPlateToRoute(
            'http://server:8080/a_step_uri', 'a_user', 'a_password', 'a_workflow_name'
        )
        self.epp._lims = Mock(get_artifacts=fake_artifacts)
        self.epp._process = Mock(all_inputs=fake_all_inputs)

    def test_discard(self):
        patched_stage = patch('EPPs.prepare_discard_plate.get_workflow_stage', return_value=Mock(uri='a_uri'))
        patched_log = patch('EPPs.prepare_discard_plate.FindPlateToRoute.info')

        exp_log_messages = (
            ('Found Stage %s uri: %s', 'Discard Plates EG 1.0', 'a_uri'),
            ('Found %d Samples in the step', 2),
            ('Found %d Analytes (derived samples)', 2),
            ('Found %d containers', 2),
            ('Found %d valid containers to potentially discard', 2),
            ('Found %d others associated with the container but not associated with discarded samples', 4),
            ('Test container %s, with %s artifacts', 'Container s1', 2),
            (
                "Container: %s won't route because artifact %s in step_associated_artifacts (%s) or has been discarded before (%s)",
                'Container s1',
                'Container s1 placement 2',
                False,
                False
            ),
            ('Route %s containers with %s artifacts', 0, 0)
        )

        with patched_log as l, patched_stage as p:
            self.epp._run()
            p.assert_called_with(self.epp.lims, workflow_name='Discard Plates EG 1.0', stage_name='Discard Plates EG 1.0')
            for m in exp_log_messages:
                l.assert_any_call(*m)


def test_fetch_all_artifacts_for_samples():
    lims = Mock(get_artifacts=Mock(return_value=[1, 2, 3]))
    # 100 samples passed in, window size = 50, so lims should be called twice
    samples = [Mock(id=str(x)) for x in range(100)]
    limsids = [s.id for s in samples]
    assert prepare_discard_plate.fetch_all_artifacts_for_samples(lims, samples) == [1, 2, 3, 1, 2, 3]
    lims.get_artifacts.assert_any_call(samplelimsid=limsids[0:50], type='Analyte')
    lims.get_artifacts.assert_any_call(samplelimsid=limsids[50:100], type='Analyte')


def test_is_valid_container():
    valid_container = FakeEntity(name='this')
    invalid_container = FakeEntity(name='this-QNT')
    flowcell = FakeEntity(name='this', type=FakeEntity(name='Patterned Flowcell'))
    assert prepare_discard_plate.is_valid_container(valid_container)
    assert not prepare_discard_plate.is_valid_container(invalid_container)
    assert not prepare_discard_plate.is_valid_container(flowcell)


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
