import hashlib
import os
from collections import Counter, defaultdict
from itertools import cycle, product
from os.path import join, dirname, abspath
from xml.etree import ElementTree

import pytest
from pyclarity_lims.constants import nsmap
from pyclarity_lims.entities import Process, Artifact, Sample, Container, Containertype, Project, Step, \
    StepPlacements, StepReagentLots, StepActions, StepDetails
from requests import ConnectionError
from unittest.case import TestCase
from unittest.mock import Mock, PropertyMock, patch, MagicMock
import EPPs
from EPPs.common import StepEPP, RestCommunicationEPP, find_newest_artifact_originating_from, InvalidStepError


class NamedMock(Mock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        real_name = kwargs.get('real_name')
        if real_name:
            self.name = real_name


def _resolve_next(o):
    """returns the next element if an iterable or return itself otherwise. list should be passed using cycle(list)"""
    if hasattr(o, '__next__'):
        return next(o)
    return o


def fake_artifact(_id):
    return Mock(
        id=str(_id),
        workflow_stages_and_statuses=[(Mock(uri='a_uri'), 'COMPLETE', 'stage1')]
    )


def fake_all_inputs(unique=False, resolve=False):
    """Return a list of mocked artifacts which contain samples which contain artifacts... Simple!"""
    return (
        Mock(samples=[Mock(artifact=fake_artifact('a1'), id='s1')]),
        Mock(samples=[Mock(artifact=fake_artifact('a2'), id='s2')])
    )


def fake_lims_get_uri(*args):
    """Small function to replace lims.get_uri"""
    return ''.join(args)


class FakeEntitiesMaker:
    def __init__(self):
        # Create a fake lims to prevent any attempt to connect to the LIMS.
        self.lims = MagicMock(cache={}, get_uri=fake_lims_get_uri)
        self.uri_counter = Counter()
        self.object_store = {}
        self.object_store_per_type = defaultdict(list)

    def _get_uri(self, klass):
        self.uri_counter[klass] += 1
        return 'uri_%s_%s' % (klass.__name__.lower(), self.uri_counter[klass])

    def _store_object(self, instance):
        self.object_store[instance.uri]=instance
        self.object_store_per_type[instance.__class__.__name__].append(instance)

    def _retrieve_object(self, uri):
        return self.object_store.get(uri)

    def _add_udfs(self, instances, udfs):
        if udfs:
            for k, v in udfs.items():
                instances.udf[k] = _resolve_next(v)

    def _find_next_positionin_container(self, container):
        if container.type.name == '96 well plate':
            plate_rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
            plate_columns = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
        elif container.type.name == 'Tube':
            plate_rows = ['1']
            plate_columns = ['1']
        elif container.type.name == '384 well plate':
            plate_rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P']
            plate_columns = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
        # search last row
        if len(container.placements) > 1:
            last_row = sorted(set([k.split(':')[0] for k in container.placements.keys()]))[-1]
            plate_rows = plate_rows[plate_rows.index(last_row):]
        for c, r in product(plate_rows, plate_columns):
            k = '%s:%s' % (c, r)
            if k not in container.placements:
                return k
        raise ValueError('No more position available for %s' % container.type.name)

    def create_instance(self, klass, uri=None, id=None, **kwargs):
        """This function create any entity instance and ensure that the root XML is populated with an empty entry."""
        # Set the prefix and tag values for the xml header
        # the actual values does not really matter since the XML won't be uploaded
        prefix = klass._PREFIX or 'stp'
        tag = klass._TAG
        if tag is None:
            tag = klass.__name__.lower()
        if uri is None:
            uri = self._get_uri(klass)
        # Check the object store first so only new object are created
        if not self._retrieve_object(uri):
            instance = klass(self.lims, uri=uri, id=id)
            instance.root = ElementTree.Element(nsmap(prefix + ':' + tag))
            for k in kwargs:
                setattr(instance, k, kwargs[k])
            self._store_object(instance)
            uri = instance.uri

        return self._retrieve_object(uri)

    def create_a_fake_project(self, project_name=None, project_udfs=None, **kwargs):
        project = self.create_instance(Project)
        if not project_name:
            project.name = project.uri
        else:
            project.name = _resolve_next(project_name)
        self._add_udfs(project, project_udfs)
        return project

    def create_fake_projects(self, nb_project=1, **kwargs):
        return [self.create_a_fake_project(**kwargs) for _ in range(nb_project)]

    def create_a_fake_container(self, container_name=None, is_output_container=False, container_udfs=None, **kwargs):
        container = self.create_instance(Container)
        if not container_name:
            prefix = 'input_'
            if is_output_container:
                prefix = 'output_'
            container.name = prefix + container.uri
        else:
            container.name = _resolve_next(container_name)
        ctype_name = _resolve_next(kwargs.get('container_type', '96 well plate'))
        container.type = self.create_instance(Containertype, name=ctype_name)
        self._add_udfs(container, container_udfs)

        return container

    def create_fake_containers(self, nb_container=1, **kwargs):
        return [self.create_a_fake_container(**kwargs) for _ in range(nb_container)]

    def create_a_fake_step(self, step_id=None, selected_containers=None, step_udfs=None, output_artifacts=None,
                           next_action=None, **kwargs):
        # Specifying Empty uri here will bypass the automatic uri generation in create_instances.
        # The uri will be generated by the Step Entity from the provided id.
        # That will ensure the Step id can be the same as the Process id.
        s = self.create_instance(Step, uri='', id=step_id)
        if selected_containers:
            s.placements = self.create_instance(StepPlacements)
            s.placements.selected_containers = selected_containers
        s._reagent_lots = self.create_instance(StepReagentLots)
        s.actions = self.create_instance(StepActions)
        if output_artifacts:
            s.actions.next_actions = [{'artifact': a} for a in output_artifacts]
            if next_action:
                for action in s.actions.next_actions:
                    action['action'] = _resolve_next(next_action)
        s.details = self.create_instance(StepDetails)
        self._add_udfs(s.details, step_udfs)
        return s

    def create_a_fake_sample(self, project, sample_name=None, sample_udfs=None, **kwargs):
        sample = self.create_instance(Sample, project=_resolve_next(project))
        sample.name = sample_name or sample.uri
        self._add_udfs(sample, sample_udfs)
        return sample

    def create_a_fake_artifact(self, artifact_name=None, artifact_position=None, artifact_type=None,
                               is_output_artifact=False, sample=None, container=None, artifact_udfs=None, **kwargs):
        c = _resolve_next(container)
        if not artifact_position:
            artifact_position = self._find_next_positionin_container(c)
        if not artifact_name:
            prefix = 'input_'
            if is_output_artifact:
                prefix = 'output_'
        artifact = self.create_instance(Artifact)
        artifact.name = prefix + 'art_' + artifact_position
        artifact.type = artifact_type
        if not sample:
            sample = self.create_a_fake_sample(**kwargs)
        sample.artifact = artifact
        artifact.samples = [sample]

        artifact.location = (c, artifact_position)
        c.placements[artifact_position] = artifact
        self._add_udfs(artifact, artifact_udfs)
        return artifact

    def create_a_fake_process(self, nb_input=1, output_per_input=1, input_name=None, output_name=None,
                              input_type='Analyte', output_type='Analyte', input_artifact_udf=None,
                              output_artifact_udf=None, **kwargs):
        """Create a fake process with some values pre-filled such as:

           - input artifacts (and associated samples/projects)
           - output artifacts
           - input container (and types)
           - output container (and types)
           - samples
           - project
           - step
        Most parameters support a list of value provided as iterable.
        Using the cycle function you can provide cycle([value1, value2])

        :param nb_input: Number of input artifact created (one sample is created per input artifact)
        :param output_per_input: Number of output artifact created per input artifact
        :param input_name: the name of the input artifact created - supports an iterable of values
        :param output_name: the name of the output artifact created - supports an iterable of values
        :param input_type: the type of input artifact created - supports an iterable of values
        :param output_type: the type of output artifact created - supports an iterable of values
        :param sample_name: the name of the sample created - supports an iterable of values
        :param sample_udfs: the udfs to be set for the samples (udfs values supports iterable)
        :param output_type: the type of output artifact created - supports an iterable of values
        :param nb_project: the number of project created (default to 1)
        :param project_udfs: the udfs to be set for the projects (udfs values supports iterable)
        :param project_name: the name of the project -- supports iterable
        :param nb_input_container: number of input container to create (default to 1)
        :param input_container_name: The name of the input container to set -- supports iterable
        :param input_container_udfs: the udfs to be set for the input container (udfs values supports iterable)
        :param nb_output_container: number of input container to create (default to 1)
        :param output_container_name: The name of the output container to set -- supports iterable
        :param output_container_udfs: the udfs to be set for the output container (udfs values supports iterable)
        :param step_udfs: the udfs to be set for the StepDetails and the Process (udfs values supports iterable)
        :param next_action: The action to set for the output artifacts -- supports iterable
        """
        # Create the projects
        projects = cycle(self.create_fake_projects(**kwargs))
        p = self.create_instance(Process, uri='p_uri')
        inputs = []
        # Create input containers
        icontainers = cycle(self.create_fake_containers(
            kwargs.get('nb_input_container', 1),
            container_name=kwargs.get('input_container_name'),
            container_udfs=kwargs.get('input_container_udfs'),
            **kwargs))
        used_input_containers = set()
        # Create Artifacts
        for n in range(nb_input):
            a = self.create_a_fake_artifact(is_output_artifact=False, artifact_name=_resolve_next(input_name),
                                            artifact_type=_resolve_next(input_type), artifact_udfs=input_artifact_udf,
                                            project=projects, container=icontainers, **kwargs)
            used_input_containers.add(a.container)
            inputs.append(a)
        outputs = []
        # Create output containers
        ocontainers = cycle(self.create_fake_containers(
            kwargs.get('nb_output_container', 1),
            container_name=kwargs.get('output_container_name'),
            container_udfs= kwargs.get('output_container_udfs'),
            is_output_container=True,
            **kwargs))
        used_output_containers = set()
        input_output_maps = []
        for a in inputs:
            input_map = {'uri': a, 'limsid': a.id, 'post-process-uri': a}
            for n in range(output_per_input):
                oa = self.create_a_fake_artifact(is_output_artifact=True, artifact_name=_resolve_next(output_name),
                                                 artifact_type=_resolve_next(output_type),
                                                 artifact_udfs=output_artifact_udf, sample=a.samples[0],
                                                 container=ocontainers, **kwargs)
                used_output_containers.add(oa.container)
                outputs.append(oa)
                output_map = {'uri': oa, 'limsid': oa.id, 'output-generation-type': 'PerInput', 'output-type': _resolve_next(output_type)}
                input_output_maps.append((input_map, output_map))
        p.input_output_maps = input_output_maps
        # Mock those two functions because they create new Artifact instead of returning the already created ones
        p.all_inputs = Mock(return_value=inputs)
        p.all_outputs = Mock(return_value=outputs)
        self._add_udfs(p, kwargs.get('step_udfs'))
        # Can't assign the step to the process but they are linked because they use the same id.
        step = self.create_a_fake_step(step_id=p.id, selected_containers=list(used_output_containers),
                                       output_artifacts=outputs, **kwargs)
        return p


class TestCommon(TestCase):
    assets = join(dirname(abspath(__file__)), 'assets')
    etc_path = join(abspath(dirname(EPPs.__file__)), 'etc')
    genotype_quantstudio = join(assets, 'YOA15_QuantStudio 12K Flex_export.txt')
    log_file = join(assets, 'test_log_file.txt')


class TestEPP(TestCommon):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.patched_lims = patch.object(StepEPP, 'lims', new_callable=PropertyMock())
        self.default_argv = [
            '--step_uri', 'http://server:8080/a_step_uri',
            '--username', 'a_user',
            '--password', 'a_password',
            '--log_file', TestCommon.log_file
        ]
        os.environ['CLARITYSCRIPTCONFIG'] = join(self.etc_path, 'example_clarity_script.yml')

    def setUp(self):
        argv = self.default_argv.copy()
        argv[1] = 'http://server:8080/some/extra/stuff'
        self.epp = StepEPP(argv)

    def test_init(self):
        assert self.epp.baseuri == 'http://server:8080'

    @staticmethod
    def stripped_md5(fname):
        hash_md5 = hashlib.md5()
        with open(fname, 'rb') as f:
            for line in f:
                hash_md5.update(line.strip())
        return hash_md5.hexdigest()

    @staticmethod
    def file_content(fname):
        file_content = []
        with open(fname, 'r') as f:
            for l in f:
                file_content.append(l.strip())
        return file_content

    def _test_replicate_per_input(self, output_per_input):
        fem = FakeEntitiesMaker()
        self.epp.lims = fem.lims
        self.epp.process = fem.create_a_fake_process(output_per_input=output_per_input)
        with pytest.raises(InvalidStepError) as e:
            self.epp._validate_step()
        assert e.value.message == "%s replicates required for each input. %s replicates found for uri_artifact_1." % (
            self.epp._nb_artifact_per_input, output_per_input
        )

    def _test_max_input_container(self, nb_input_container):
        fem = FakeEntitiesMaker()
        self.epp.lims = fem.lims
        self.epp.process = fem.create_a_fake_process(nb_input=nb_input_container,
                                                     nb_input_container=nb_input_container)
        with pytest.raises(InvalidStepError) as e:
            self.epp._validate_step()
        assert e.value.message == "Maximum number of input container is %s. There are %s input container in the step." % (
            self.epp._max_nb_input_containers, nb_input_container
        )

    def _test_max_output_container(self, nb_output_container):
        fem = FakeEntitiesMaker()
        self.epp.lims = fem.lims
        self.epp.process = fem.create_a_fake_process(nb_input=nb_output_container,
                                                     nb_output_container=nb_output_container)
        with pytest.raises(InvalidStepError) as e:
            self.epp._validate_step()
        print(e.value.message)
        assert e.value.message == "Maximum number of output plates is %s. There are %s output plates in the step." % (
            self.epp._max_nb_output_containers, nb_output_container
        )

    def _test_max_nb_input(self, nb_input):
        fem = FakeEntitiesMaker()
        self.epp.lims = fem.lims
        self.epp.process = fem.create_a_fake_process(nb_input=nb_input)
        with pytest.raises(InvalidStepError) as e:
            self.epp._validate_step()
        assert e.value.message == "Maximum number of inputs is %s. %s inputs present in step." % (
            self.epp._max_nb_input, nb_input
        )

    def _test_nb_project(self, nb_project):
        fem = FakeEntitiesMaker()
        self.epp.lims = fem.lims
        self.epp.process = fem.create_a_fake_process(nb_input=nb_project, nb_project=nb_project)
        with pytest.raises(InvalidStepError) as e:
            self.epp._validate_step()
        assert e.value.message == "Maximum number of projet in step is %s. %s projects found." % (
            self.epp._max_nb_project, nb_project
        )


class TestStepEPP(TestEPP):

    def test_replicate_per_input(self):
        # 3 replicates outputs rather than required 2 per input
        self.epp._nb_artifact_per_input = 2
        self._test_replicate_per_input(output_per_input=3)

    def test_max_input_container(self):
        # 1 container is allowed and 2 are created
        self.epp._max_nb_input_containers = 1
        self._test_max_input_container(nb_input_container=2)

    def test_max_output_container(self):
        # 1 output container is allowed and 2 are created
        self.epp._max_nb_output_containers = 1
        self._test_max_output_container(nb_output_container=2)

    def test_max_nb_input(self):
        # 24 inputs are allowed and 25 are present
        self.epp._max_nb_input = 24
        self._test_max_nb_input(nb_input=25)

    def test_nb_project(self):
        # 1 projects are allowed and 2 are present
        self.epp._max_nb_project = 1
        self._test_nb_project(nb_project=2)


class TestRestCommunicationEPP(TestCase):
    @staticmethod
    def fake_rest_interaction(*args, **kwargs):
        if kwargs.get('dodgy'):
            raise ConnectionError('Something broke!')
        return args, kwargs

    def test_interaction(self):
        epp = RestCommunicationEPP()
        assert epp._rest_interaction(self.fake_rest_interaction, 'this', 'that', other='another') == (
            ('this', 'that'), {'other': 'another'}
        )

        with patch('sys.exit') as mocked_exit, patch('builtins.print') as mocked_print:
            epp._rest_interaction(self.fake_rest_interaction, 'this', 'that', dodgy=True)

        mocked_exit.assert_called_with(127)
        mocked_print.assert_called_with('ConnectionError: Something broke!')


class TestFindNewestArtifactOriginatingFrom(TestCase):
    def test_find_newest_artifact_originating_from(self):
        lims = Mock()
        lims.get_artifacts.return_value = [
            Mock(id='fx1', parent_process=Mock(id='121')),
            Mock(id='fx2', parent_process=Mock(id='123'))
        ]
        process_type = 'Process 1.0'
        sample_name = 's1'
        artifact = find_newest_artifact_originating_from(lims, process_type, sample_name)
        assert artifact.id == 'fx2'
        lims.get_artifacts.assert_called_with(type='Analyte', process_type='Process 1.0', sample_name='s1')

        lims.get_artifacts.return_value = [
            Mock(id='fx1', parent_process=Mock(id='121')),
        ]
        artifact = find_newest_artifact_originating_from(lims, process_type, sample_name)
        assert artifact.id == 'fx1'

        lims.get_artifacts.return_value = []
        artifact = find_newest_artifact_originating_from(lims, process_type, sample_name)
        assert artifact is None