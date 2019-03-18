from os.path import join, dirname, abspath
from unittest.mock import Mock, patch

from scripts import spectramax_sample_quant
from tests.test_common import TestEPP, NamedMock


class TestSpectramaxOutput(TestEPP):
    exp_concs = {
        1: ('A1', 1951.380), 2: ('A2', 1682.999), 9: ('B1', 1519.252), 10: ('B2', 1562.669), 11: ('B3', 1529.251),
        12: ('A1', 1607.848), 13: ('A2', 1645.374), 14: ('A3', 1559.238), 15: ('B1', 1470.509), 3: ('A3', 1686.545),
        4: ('B1', 1504.041), 5: ('B2', 1409.417), 6: ('A1', 1415.035), 7: ('A2', 1470.661), 8: ('A3', 1468.779)
    }

    exp_plates = {
        'a_plate': {'A1': 1951.38, 'A2': 1682.999, 'A3': 1686.545, 'B1': 1504.041, 'B2': 1409.417},
        'another_plate': {'A1': 1415.035, 'A2': 1470.661, 'A3': 1468.779, 'B1': 1519.252, 'B2': 1562.669, 'B3': 1529.251},
        'yet_another_plate': {'A1': 1607.848, 'A2': 1645.374, 'A3': 1559.238, 'B1': 1470.509}
    }

    exp_plate_names = ['a_plate', 'another_plate', 'yet_another_plate']

    def setUp(self):

        self.epp = spectramax_sample_quant.SpectramaxOutput(
            self.default_argv + [
                '--spectramax_file',
                join(dirname(abspath(__file__)), 'assets', 'spectramax_output.txt')
            ]
        )

    def test_parse_spectramax_file(self):
        self.epp.parse_spectramax_file()
        assert self.epp.plate_names == self.exp_plate_names
        assert self.epp.sample_concs == self.exp_concs

    def test_assign_samples_to_plates(self):
        self.epp.plate_names = self.exp_plate_names
        self.epp.sample_concs = self.exp_concs.copy()
        self.epp.assign_samples_to_plates()

        assert self.epp.plates == self.exp_plates

        self.epp.plates.clear()

        del self.epp.sample_concs[6]
        with self.assertRaises(AssertionError) as e:
            self.epp.assign_samples_to_plates()
        assert str(e.exception) == 'Badly formed spectramax file: tried to add coord A2 for sample 7 to plate a_plate'

    @patch('scripts.spectramax_sample_quant.SpectramaxOutput.process')
    def test_add_plates_to_step(self, mocked_process):
        fake_placements = []
        for plate in self.exp_plate_names:
            for x in 'ABCDEFGH':
                for y in range(1, 13):
                    placement = (Mock(udf={}), (NamedMock(real_name=plate), x + ':' + str(y)))
                    fake_placements.append(placement)

        assert len(fake_placements) == 3 * 96

        self.epp.plates = self.exp_plates.copy()
        mocked_process.step = Mock(placements=Mock(get_placement_list=Mock(return_value=fake_placements)))
        self.epp._add_plates_to_step()

        for artifact, (container, coord) in fake_placements:
            coord = coord.replace(':', '')
            if coord in self.epp.plates[container.name]:
                assert artifact.udf == {
                    'Raw Value': self.epp.plates[container.name][coord],
                }
