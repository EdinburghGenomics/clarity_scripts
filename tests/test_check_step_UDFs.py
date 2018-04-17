import os
import platform
from egcg_core.config import cfg
from scripts.check_step_UDFs import CheckStepUDFs
from tests.test_common import TestEPP, NamedMock
from unittest.mock import Mock, patch, PropertyMock


class TestCheckStepUDFs(TestEPP):

    def setUp(self):
        super().setUp()
        self.epp = self.create_epp(CheckStepUDFs)
        self.patch_process = self.create_patch_process(
            TestCheckStepUDFs,
            {
                'Udfname1': 'John Doe',
                'Udfname2': 'Jane Doe',
            }
        )
    def test_check_syep_UDFs(self):
        with self.patch_process:
            self.epp._run()



