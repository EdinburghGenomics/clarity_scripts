from datetime import date
from unittest.mock import patch

from scripts.populate_pool_batch_and_pools import PopulatePoolBatchPools
from tests.test_common import NamedMock
from tests.test_common import TestEPP, FakeEntitiesMaker, Mock


class TestPopulatePoolBatchPools(TestEPP):
    # @staticmethod
    # def get_patch_create_container(container):
    #     return patch().object(Container, 'create', return_value=container)

    def setUp(self):


        self.epp = PopulatePoolBatchPools(self.default_argv)
        self.fem = FakeEntitiesMaker()
        self.today = str(date.today())
        containers = iter(
            [[Mock(return_value=[])]])
        self.patched_get_containers = patch('pyclarity_lims.lims.Lims.get_containers',
                                               side_effect=containers)
        self.fem_params = {
            'nb_input': 1,
            'input_reagent_label': 'Adapter1',
            'project_name': 'X99999',
            'sample_udfs': {
                'Prep Workflow': 'TruSeq Nano DNA Sample Prep',
            }
        }

    def test_populate_pool_batch_and_pools_no_existing_objects(self):
        self.epp.lims = self.fem.lims
        self.epp.process = self.fem.create_a_fake_process(**self.fem_params)
        self.epp.lims.get_containers = Mock(return_value=[])
        self.epp.lims.get_artifacts = Mock(return_value=[])
        self.epp.lims.get_reagent_types = Mock(return_value=[Mock(category='rt1')])
        self.epp._run()

        expected_output_container_name = 'PDP_Batch_ID:_'+self.today+'_PDP_Batch#1'
        actual_output_container_name = self.epp.process.analytes()[0][0].container.name

        expected_output_pool_name = self.today + '_PDP_Pool#1'
        actual_output_pool_name = self.epp.process.analytes()[0][0].name

        expected_output_udfs = {'Prep Workflow': 'TruSeq Nano DNA Sample Prep', 'Adapter Type': 'rt1'}
        actual_output_udfs = self.epp.process.analytes()[0][0].udf


        assert actual_output_container_name == expected_output_container_name
        assert actual_output_pool_name == expected_output_pool_name
        assert actual_output_udfs == expected_output_udfs



