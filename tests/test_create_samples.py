from unittest.mock import patch, Mock

from pyclarity_lims.entities import Sample

from scripts.create_samples import CreateSamples, Container
from tests.test_common import TestEPP, FakeEntitiesMaker


class TestCreateSamples(TestEPP):
    patched_get_workflow_stage = patch('scripts.create_samples.get_workflow_stage', return_value=Mock(uri='a_uri'))
    patched_create_batch = patch('lims.create_samples.create_batch', return_value=True)
    patched_get_documents = patch('egcg_core.rest_communication.get_documents', return_value=[{"name": "Homo sapiens"}])

    @staticmethod
    def get_patch_create_container(container):
        return patch.object(Container, 'create', return_value=container)

    def setUp(self):
        self.epp = CreateSamples(self.default_argv)
        self.fem_params = {
            'project_name': 'X99999',
            'input_container_name': 'X99999P001',
            'sample_name': 'X99999P001A01',
            'output_per_input': 0,
            'step_udfs': {
                'Container Type': '96 well plate',
                'Plate Suffix': 'P[0-9]{3}',
                'Number in Group 1': 1,
                'Number in Group 2': 0,
                'Number in Group 3': 0,
                'Number in Group 4': 0,
                '[C]Prep Workflow': 'TruSeq Nano DNA Sample Prep',
                '[G]Coverage (X)(1)': 30,
                '[G]Species(1)': 'Homo sapiens',
                'Next Workflow': 'A workflow',
                'Next Step': 'A step'
            }
        }

    def test_next_sample_name_and_pos(self):
        fem = FakeEntitiesMaker()
        self.epp.lims = fem.lims
        self.epp.process = fem.create_a_fake_process(**self.fem_params)
        self.epp.lims.get_containers = Mock(return_value=[])
        with self.get_patch_create_container(fem.create_a_fake_container(container_name='X99999P002')) as mcreate:
            sample_name, sample_position = self.epp._next_sample_name_and_pos()
            assert sample_name == 'X99999P001A01'
            assert sample_position == 'A:1'
            for i in range(95):
                sample_name, sample_position = self.epp._next_sample_name_and_pos()
            assert sample_name == 'X99999P001H12'
            assert sample_position == 'H:12'

            assert mcreate.call_count == 0
            sample_name, sample_position = self.epp._next_sample_name_and_pos()
            assert sample_name == 'X99999P002A01'
            assert sample_position == 'A:1'
            assert mcreate.call_count == 1

    def test_create_sample_dict(self):
        fem = FakeEntitiesMaker()
        self.epp.lims = fem.lims
        self.fem_params['step_udfs']['[G]Coverage (X)(2)'] = 60
        self.fem_params['step_udfs']['[G]Coverage (X)(3)'] = 90
        self.fem_params['step_udfs']['[G]Coverage (X)(4)'] = 120
        self.epp.process = fem.create_a_fake_process(**self.fem_params)

        expected_dict = {
            'name': 'X99999P001A01', 'container': fem.object_store_per_type['Container'][0], 'position': 'A:1',
            'project': fem.object_store_per_type['Project'][0],
            'udf': {'Prep Workflow': 'TruSeq Nano DNA Sample Prep', 'Coverage (X)': 30, 'Species': 'Homo sapiens'}
        }

        # test parsing all 4 groups
        assert self.epp._create_sample_dict(1) == expected_dict
        assert self.epp._create_sample_dict(2)['udf']['Coverage (X)'] == 60
        assert self.epp._create_sample_dict(3)['udf']['Coverage (X)'] == 90
        assert self.epp._create_sample_dict(4)['udf']['Coverage (X)'] == 120

    def test_create_sample_96_well_plate_1_sample(self):  # no new samples created, input sample populated by step UDFs
        fem = FakeEntitiesMaker()
        self.epp.lims = fem.lims
        # Add genome version
        self.fem_params['step_udfs']['[G]Genome Version(1)'] = 'hg38'
        self.epp.process = fem.create_a_fake_process(**self.fem_params)

        with self.patched_get_workflow_stage, self.patched_get_documents as mgetdoc:
            self.epp._validate_step()
            self.epp._run()
        # UDFs have been applied
        assert self.epp.samples[0].udf == {
            'Coverage (X)': 30,
            'Prep Workflow': 'TruSeq Nano DNA Sample Prep',
            'Species': 'Homo sapiens',
            'Genome Version': 'hg38'
        }
        # sample has been uploaded
        assert self.epp.lims.put.call_count == 1
        # REST API was contacted
        mgetdoc.assert_any_called_with('species', where={'name': 'Homo sapiens'})
        mgetdoc.assert_any_called_with('genomes', where={'assembly_name': 'hg38'})
        assert mgetdoc.call_count == 2

    def test_create_sample_96_well_plate_4_samples(self):
        """ Test how 4 new samples are created"""
        fem = FakeEntitiesMaker()
        self.epp.lims = fem.lims
        self.fem_params['step_udfs']['Number in Group 1'] = 5
        self.epp.process = fem.create_a_fake_process(**self.fem_params)
        # getting new container (when searching for container names) returns the second name as not existing
        self.epp.lims.get_containers = Mock(side_effect=[True, False])

        with self.get_patch_create_container(fem.create_a_fake_container(container_name='X99999P002')) as mcreate, \
                self.patched_get_workflow_stage, self.patched_get_documents:
            self.epp._validate_step()
            self.epp._run()

        udfs_g1 = {'Prep Workflow': 'TruSeq Nano DNA Sample Prep', 'Coverage (X)': 30, 'Species': 'Homo sapiens'}
        p = fem.object_store_per_type['Project'][0]
        c = fem.object_store_per_type['Container'][0]
        # Fill up the container by column first
        expected_list = [
            {'position': 'B:1', 'name': 'X99999P001B01', 'project': p, 'udf': udfs_g1, 'container': c},
            {'position': 'C:1', 'name': 'X99999P001C01', 'project': p, 'udf': udfs_g1, 'container': c},
            {'position': 'D:1', 'name': 'X99999P001D01', 'project': p, 'udf': udfs_g1, 'container': c},
            {'position': 'E:1', 'name': 'X99999P001E01', 'project': p, 'udf': udfs_g1, 'container': c},
        ]
        self.epp.lims.create_batch.assert_called_once_with(Sample, expected_list)
        # One call to retrieve the samples at the start and at the end when the samples are updated
        assert self.epp.lims.get_batch.call_count == 2
        assert self.epp.lims.route_artifacts.call_count == 1

        # No new plate were created
        assert mcreate.call_count == 0

    def test_create_sample_96_well_plate_100_new_samples(self):
        """ Test how 100  new samples are created across 4 groups"""
        fem = FakeEntitiesMaker()
        self.epp.lims = fem.lims
        self.fem_params['step_udfs']['Number in Group 1'] = 25
        self.fem_params['step_udfs']['Number in Group 2'] = 25
        self.fem_params['step_udfs']['[G]Coverage (X)(2)'] = 60
        self.fem_params['step_udfs']['Number in Group 3'] = 25
        self.fem_params['step_udfs']['[G]Coverage (X)(3)'] = 90
        self.fem_params['step_udfs']['Number in Group 4'] = 25
        self.fem_params['step_udfs']['[G]Coverage (X)(4)'] = 120
        self.epp.process = fem.create_a_fake_process(**self.fem_params)
        # getting new container (when searching for container names) returns the second name as not existing
        self.epp.lims.get_containers = Mock(side_effect=[True, False])

        with self.get_patch_create_container(fem.create_a_fake_container(container_name='X99999P002')) as mcreate, \
                self.patched_get_workflow_stage, self.patched_get_documents:
            self.epp._validate_step()
            self.epp._run()

        udfs_g1 = {'Prep Workflow': 'TruSeq Nano DNA Sample Prep', 'Coverage (X)': 30, 'Species': 'Homo sapiens'}
        udfs_g2 = {'Prep Workflow': 'TruSeq Nano DNA Sample Prep', 'Coverage (X)': 60}
        udfs_g3 = {'Prep Workflow': 'TruSeq Nano DNA Sample Prep', 'Coverage (X)': 90}
        udfs_g4 = {'Prep Workflow': 'TruSeq Nano DNA Sample Prep', 'Coverage (X)': 120}
        p = fem.object_store_per_type['Project'][0]
        c1 = fem.object_store_per_type['Container'][0]
        c2 = fem.object_store_per_type['Container'][1]
        # Fill up the container by column first

        # expect 1 sample updated + 99 samples created
        # 96 first samples are on container1 and next 4 are in container2
        expected_list = \
            [dict(project=p, name='X99999P001%s%02d' % (c, r), udf=udfs_g1, position='%s:%s' % (c, r), container=c1) for
             r, c in self.epp.plate96_layout[1: 25]] + \
            [dict(project=p, name='X99999P001%s%02d' % (c, r), udf=udfs_g2, position='%s:%s' % (c, r), container=c1) for
             r, c in self.epp.plate96_layout[25: 50]] + \
            [dict(project=p, name='X99999P001%s%02d' % (c, r), udf=udfs_g3, position='%s:%s' % (c, r), container=c1) for
             r, c in self.epp.plate96_layout[50: 75]] + \
            [dict(project=p, name='X99999P001%s%02d' % (c, r), udf=udfs_g4, position='%s:%s' % (c, r), container=c1) for
             r, c in self.epp.plate96_layout[75:]] + \
            [dict(project=p, name='X99999P002%s%02d' % (c, r), udf=udfs_g4, position='%s:%s' % (c, r), container=c2) for
             r, c in self.epp.plate96_layout[:4]]

        self.epp.lims.create_batch.assert_called_once_with(Sample, expected_list)

        # A new plate was created
        assert mcreate.call_count == 1
