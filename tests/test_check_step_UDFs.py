from scripts.check_step_UDFs import CheckStepUDFs
from tests.test_common import TestEPP
from unittest.mock import Mock, patch, PropertyMock


class TestCheckStepUDFs(TestEPP):
    def setUp(self):

        self.patched_process = patch.object(
            CheckStepUDFs,
            'process',
            new_callable=PropertyMock(return_value=Mock(udf={

                'udfname1': 'a',
                'udfname2': 'a'
            }))
        )

        self.epp = CheckStepUDFs(
            'http://server:8080/a_step_uri',
            'a_user',
            'a_password',
            ['udfname1', 'udfname2'],
            self.log_file
        )

    def test_check_step_UDFs(self):
        with self.patched_process:
            self.epp._run()

