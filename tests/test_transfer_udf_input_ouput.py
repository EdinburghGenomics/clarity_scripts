from scripts.transfer_udf_input_output import TransferUDFInputOutput
from tests.test_common import TestEPP, FakeEntitiesMaker


class TestTransferUDFInputOutput(TestEPP):



    def setUp(self):
        self.epp = TransferUDFInputOutput(self.default_argv + ['-n', 'The First UDF','The Second UDF','The Third UDF'])

    def test_transfer_udf_input_output(self):
        input_udfs={'The First UDF':'The First Value',
                        'The Second UDF':'The Second Value',
                        'The Third UDF':'The Third Value'}
        fem = FakeEntitiesMaker()
        self.epp.process=fem.create_a_fake_process(input_artifact_udf=input_udfs)

        self.epp._run()

        actual_udfs = self.epp.process.outputs_per_input(self.epp.artifacts[0])[0].udf
        expected_udfs= input_udfs

        assert actual_udfs==expected_udfs
