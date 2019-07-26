from datetime import date
from unittest.mock import patch

import pytest

from EPPs.common import InvalidStepError
from scripts.populate_batch_id import PopulateBatchID
from tests.test_common import TestEPP, FakeEntitiesMaker, Mock


class TestPopulatePoolBatchID(TestEPP):
    # @staticmethod
    # def get_patch_create_container(container):
    #     return patch().object(Container, 'create', return_value=container)

    def setUp(self):
        self.epp = PopulateBatchID(self.default_argv)
        self.fem = FakeEntitiesMaker()
        self.fem_params = {
            'nb_input': 6,
            'input_reagent_label': 'Adapter1',
            'project_name': 'X99999',
            'sample_udfs': {
                'Prep Workflow': 'TruSeq Nano DNA Sample Prep',
            },
            'pool_size': 3,
        }
        self.today = str(date.today())


    def test_populate_batch_id_no_existing_objects_happy_path(self):
        self.epp.lims = self.fem.lims

        self.epp.process = self.fem.create_a_fake_process(**self.fem_params)
        self.epp.lims.get_containers = Mock(return_value=[])
        self.epp.lims.get_artifacts = Mock(return_value=[])
        self.epp.lims.get_reagent_types = Mock(return_value=[Mock(category='rt1')])

        self.epp._run()

        expected_output_container_name = self.today + '_CST_Batch#1'
        actual_output_container_name = self.epp.process.analytes()[0][0].container.name

        expected_output_udfs = {'Prep Workflow': 'TruSeq Nano DNA Sample Prep',
                                'Adapter Type': 'rt1'}

        actual_output_udfs = self.epp.process.analytes()[0][0].udf

        assert actual_output_container_name == expected_output_container_name
        assert actual_output_udfs == expected_output_udfs

    def test_create_cst_batch_id_error(self): #too many batches with today's date, limit is 999
        self.epp.lims = self.fem.lims
        with patch.object(self.epp.lims, 'get_containers', side_effect=[['a']] * 1000 + [[]]), pytest.raises(ValueError) as e:
            assert self.epp.create_cst_batch_id()
            expected_error= 'Cannot allocate more than 999 cst batch IDs with date %s' % str(date.today())
            assert str(e.value) == expected_error