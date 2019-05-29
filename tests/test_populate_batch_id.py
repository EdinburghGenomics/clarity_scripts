from datetime import date
from unittest.mock import Mock

from scripts.populate_batch_id import PopulateBatchID
from tests.test_common import TestEPP, FakeEntitiesMaker


class TestPopulateBatchID (TestEPP):

    def setUp(self):
        self.epp = PopulateBatchID(self.default_argv)
        self.fem=FakeEntitiesMaker()

    def test_no_pools(self):
        #test that CST batch ID is assigned correctly and that correct recipe is assigned for non-pooling
        self.epp.lims = self.fem.lims
        self.epp.process = self.fem.create_a_fake_process()
        self.epp.lims.get_containers = Mock(return_value=[])
        self.epp._run()

        expected_batch_id = str(date.today())+'_CST_Batch#1'
        actual_batch_id = self.epp.process.analytes()[0][0].container.name

        assert actual_batch_id == expected_batch_id

