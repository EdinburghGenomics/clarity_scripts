from scripts.check_step_UDFs import CheckStepUDFs
from tests.test_common import TestEPP
from unittest.mock import Mock, patch, PropertyMock


class TestCheckStepUDFs(TestEPP):
    def setUp(self):
        self.patched_process = patch.object(
            CheckStepUDFs,
            'process',
            new_callable=PropertyMock(return_value=Mock(udf={'udfname1': 'a', 'udfname2': 'a'}))
        )

        self.epp = CheckStepUDFs(self.default_argv + ['-n', 'udfname1', 'udfname2'])
        self.epp2 = CheckStepUDFs(self.default_argv + ['-n', 'udfname1', 'udfname2', 'udfname3'])

    def test_check_step_UDFs_success(self):
        with self.patched_process:
            # Both UDFs are present so run does not execute sys.exit
            assert self.epp._run() is None

    def test_check_step_UDFs_fail(self):
        with self.patched_process, patch('sys.exit') as mexit:
            # One UDF is missing so run will execute sys.exit
            self.epp2._run()
            mexit.assert_called_once_with(1)
