from datetime import date
from unittest.mock import Mock

from scripts.populate_batch_id_and_recipe import PopulateBatchIDRecipe
from tests.test_common import TestEPP, FakeEntitiesMaker


class TestPopulateBatchIDRecipe (TestEPP):

    def setUp(self):
        self.epp = PopulateBatchIDRecipe(self.default_argv)
        self.fem=FakeEntitiesMaker()

    def test_no_pools(self):
        self.epp.lims = self.fem.lims
        self.epp.process = self.fem.create_a_fake_process()
        self.epp.lims.get_containers = Mock(return_value=[])
        self.epp._run()

        expected_batch_id = str(date.today())+'_CST_Batch#1'
        actual_batch_id = self.epp.process.analytes()[0][0].container.name

        expected_recipe = 'HiSeqXRecipe.xml'
        actual_recipe = self.epp.process.udf['Sequencing Run Configuration']

        assert actual_batch_id == expected_batch_id
        assert actual_recipe == expected_recipe