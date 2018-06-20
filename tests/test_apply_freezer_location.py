from unittest.mock import Mock, patch, PropertyMock
from scripts.apply_freezer_location import ApplyFreezerLocation
from tests.test_common import TestEPP, NamedMock


def fake_all_inputs1(unique=False, resolve=False):
    """Return a list of mocked artifacts which contain samples which contain artifacts where container name has been
    assigned. Freezer and Shelf UDF assigned to samples. For testing UDFs are assigned correctly"""

    return (
        Mock(id='ao1', samples=[Mock(artifact=Mock(id='a1', container=NamedMock(real_name='Name1')), id='s1',
                                     udf={'Freezer': '', 'Shelf': ''})]),
        Mock(id='ao2', samples=[Mock(artifact=Mock(id='a2', container=NamedMock(real_name='Name1')), id='s2',
                                     udf={'Freezer': '', 'Shelf': ''})])
    )


def fake_all_inputs2(unique=False, resolve=False):
    """Return a list of mocked artifacts which contain samples which contain artifacts where container name has been
    assigned. Freezer and Shelf UDF assigned to samples. For testing that a system exit occurs if container in step UDF
    does not match the name of the sample artifact container"""

    return (
        Mock(id='ao1', samples=[Mock(artifact=Mock(id='a1', container=NamedMock(real_name='Name1')), id='s1',
                                     udf={'Freezer': '', 'Shelf': ''})]),
        Mock(id='ao2', samples=[Mock(artifact=Mock(id='a2', container=Mock(containername='Name2')), id='s2',
                                     udf={'Freezer': '', 'Shelf': ''})])
    )


class TestApplyFreezerLocation(TestEPP):
    def setUp(self):
        step_udfs = {
            'Container Name': 'Name1',
            'Freezer': 'Freezer1',
            'Shelf': 'Shelf1',
        }
        self.patched_process1 = patch.object(
            ApplyFreezerLocation,
            'process', new_callable=PropertyMock(return_value=Mock(all_inputs=fake_all_inputs1, udf=step_udfs))
        )

        self.patched_process2 = patch.object(
            ApplyFreezerLocation,
            'process', new_callable=PropertyMock(return_value=Mock(all_inputs=fake_all_inputs2, udf=step_udfs))
        )

        self.epp = ApplyFreezerLocation(self.default_argv)

    def test_udf_update(self):  # test UDFs are assigned
        with self.patched_lims, self.patched_process1:
            self.epp._run()

            # test that sample UDFs Freezer and Shelf are updated to match step UDFs Freezer and Shelf
            assert self.epp.artifacts[0].samples[0].artifact.container.name == self.epp.process.udf['Container Name']
            assert self.epp.artifacts[0].samples[0].udf['Freezer'] == self.epp.process.udf['Freezer']
            assert self.epp.artifacts[0].samples[0].udf['Shelf'] == self.epp.process.udf['Shelf']

    def test_container_absent(self):  # test system exist occurs if container in step does not match sample artifact
        with self.patched_lims, self.patched_process2, patch('sys.exit') as mexit:
            self.epp._run()

            mexit.assert_called_once_with(1)
