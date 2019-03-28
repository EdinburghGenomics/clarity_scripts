from os.path import join
from unittest.mock import patch

import pytest

from EPPs.common import InvalidStepError
from scripts.parse_manifest import ParseManifest
from tests.test_common import TestEPP, FakeEntitiesMaker


class TestParseManifest(TestEPP):
    process_udfs = {
        'Plate Sample Name': 'A',
        '[Plate]Container Name': 'B',
        '[Plate]Well': 'C',
        'Plate Starting Row': 1,
    }

    def setUp(self):
        super().setUp()
        self.fem = FakeEntitiesMaker()
        self.process = self.fem.create_a_fake_process(
            nb_input=2, sample_name=iter(['Key1', 'Key2']), step_udfs=self.process_udfs
        )

    def test_parse_manifest_happy_path(self):
        epp = ParseManifest(self.default_argv + ['--manifest', join(self.assets, 'Manifest_To_Parse.xlsx')])
        epp.lims = self.fem.lims
        epp.process = self.process
        with patch.object(ParseManifest, 'warning') as mwarning:
            epp._run()
        # Check the udfs have been updated in the samples
        assert [s.udf for s in epp.samples] == [{'Container Name': 'Value1'}, {'Container Name': 'Value2'}]
        # Check that the warning were logged
        mwarning.assert_any_call('Value UDF %s is not set for sample %s (cell %s).', 'Well', 'Key1', 'C1')
        mwarning.assert_any_call('Value UDF %s is not set for sample %s (cell %s).', 'Well', 'Key2', 'C2')
        # Check the samples have been uploaded
        epp.lims.put_batch.assert_called_once_with(epp.samples)

    def test_parse_manifest_sample_too_many(self):
        epp = ParseManifest(self.default_argv + ['--manifest', join(self.assets, 'Manifest_To_Parse_too_many.xlsx')])
        epp.lims = self.fem.lims
        epp.process = self.process
        with pytest.raises(InvalidStepError) as e:
            epp._run()
        assert str(e.value) == 'Key3 present in manifest but not present in LIMS.'

    def test_parse_manifest_sample_too_few(self):
        epp = ParseManifest(self.default_argv + ['--manifest', join(self.assets, 'Manifest_To_Parse_too_few.xlsx')])
        epp.lims = self.fem.lims
        epp.process = self.process
        with pytest.raises(InvalidStepError) as e:
            epp._run()
        assert str(e.value) == 'The number of samples in the step does not match the number of samples in the manifest'
