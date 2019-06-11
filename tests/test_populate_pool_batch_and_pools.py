from datetime import date
from itertools import cycle
from unittest.mock import patch

import pytest

from EPPs.common import InvalidStepError
from scripts.populate_pool_batch_and_pools import PopulatePoolBatchPools
from tests.test_common import TestEPP, FakeEntitiesMaker, Mock


class TestPopulatePoolBatchPools(TestEPP):
    # @staticmethod
    # def get_patch_create_container(container):
    #     return patch().object(Container, 'create', return_value=container)

    def setUp(self):
        self.epp = PopulatePoolBatchPools(self.default_argv)
        self.fem = FakeEntitiesMaker()
        self.fem_params = {
            'nb_input': 6,
            'input_reagent_label': 'Adapter1',
            'project_name': 'X99999',
            'sample_udfs': {
                'Prep Workflow': 'TruSeq Nano DNA Sample Prep',
                'Remaining Yield (Gb)': 40
            },
            'pool_size': 3,
        }
        self.today = str(date.today())


    def test_populate_pool_batch_and_pools_no_existing_objects_happy_path(self):
        self.epp.lims = self.fem.lims

        self.epp.process = self.fem.create_a_fake_process(**self.fem_params)
        self.epp.lims.get_containers = Mock(return_value=[])
        self.epp.lims.get_artifacts = Mock(return_value=[])
        self.epp.lims.get_reagent_types = Mock(return_value=[Mock(category='rt1')])

        self.epp._run()

        expected_output_container_name = self.today + '_PDP_Batch#1'
        actual_output_container_name = self.epp.process.analytes()[0][0].container.name

        expected_output_pool_name = self.today + '_PDP_Pool#1'
        actual_output_pool_name = self.epp.process.analytes()[0][0].name

        expected_output_udfs = {'Prep Workflow': 'TruSeq Nano DNA Sample Prep',
                                'Adapter Type': 'rt1', 'NTP Volume (uL)': 5.0, 'Number of Lanes': 1.0}

        actual_output_udfs = self.epp.process.analytes()[0][0].udf

        assert actual_output_container_name == expected_output_container_name
        assert actual_output_pool_name == expected_output_pool_name
        assert actual_output_udfs == expected_output_udfs

    def test_populate_pool_batch_and_pools_low_ntp_volume(self):
        self.epp.lims = self.fem.lims
        fem_params = self.fem_params
        fem_params['nb_input']=20
        fem_params['sample_udfs']['Remaining Yield (Gb)']= 10
        fem_params['pool_size']= 10

        self.epp.process = self.fem.create_a_fake_process(**fem_params)
        self.epp.lims.get_containers = Mock(return_value=[])
        self.epp.lims.get_artifacts = Mock(return_value=[])
        self.epp.lims.get_reagent_types = Mock(return_value=[Mock(category='rt1')])
        with pytest.raises(InvalidStepError) as e:
            self.epp._run()

        assert str(e.value) == 'NTP Volume (uL) cannot be less than 2. NTP Volume (uL) for libraries in output_art_A:1 is 1.5'

    def test_create_pool_id_error(self): #too many pools with today's date, limit is 999
        self.epp.lims = self.fem.lims

        with patch.object(self.epp.lims, 'get_containers', side_effect=[['a']] * 1000 + [[]]), pytest.raises(InvalidStepError) as e:
            assert self.epp.create_pool_id()
        assert str(e.value) == 'Cannot allocate more than 999 pool IDs with date %s' % str(date.today())

    def test_create_pool_batch_id_error(self): #too many batches with today's date, limit is 999
        self.epp.lims = self.fem.lims

        with patch.object(self.epp.lims, 'get_containers', side_effect=[['a']] * 1000 + [[]]), pytest.raises(InvalidStepError) as e:
            assert self.epp.create_pool_batch_id()
        assert str(e.value) == 'Cannot allocate more than 999 pool batch IDs with date %s' % str(date.today())
