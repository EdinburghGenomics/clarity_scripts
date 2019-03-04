from os.path import join, dirname, abspath
from unittest.mock import Mock, patch
from scripts.spectramax import SpectramaxOutput
from scripts import spectramax
from tests.test_common import TestEPP, NamedMock


class TestSpectramaxOutput(TestEPP):
    exp_concs = {
        1: ('A1', 55.107), 2: ('A2', 47.653), 9: ('B1', 43.105), 10: ('B2', 44.311), 11: ('B3', 43.383),
        12: ('A1', 45.566), 13: ('A2', 46.608), 14: ('A3', 44.216), 15: ('B1', 41.752), 3: ('A3', 47.752),
        4: ('B1', 42.683), 5: ('B2', 40.055), 6: ('A1', 40.211), 7: ('A2', 41.756), 8: ('A3', 41.704)
    }

    exp_plates = {
        'a_plate': {'A1': 55.107, 'A2': 47.653, 'A3': 47.752, 'B1': 42.683, 'B2': 40.055},
        'another_plate': {'A1': 40.211, 'A2': 41.756, 'A3': 41.704, 'B1': 43.105, 'B2': 44.311, 'B3': 43.383},
        'yet_another_plate': {'A1': 45.566, 'A2': 46.608, 'A3': 44.216, 'B1': 41.752}
    }

    exp_plate_names = ['a_plate', 'another_plate', 'yet_another_plate']




    def setUp(self):

        self.epp = spectramax.SpectramaxOutput(
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

    @patch('scripts.spectramax.SpectramaxOutput.process')
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
        self.epp.add_plates_to_step()

        for artifact, (container, coord) in fake_placements:
            coord = coord.replace(':', '')
            if coord in self.epp.plates[container.name]:
                assert artifact.udf == {
                    'Unadjusted Pico Conc (ng/ul)': self.epp.plates[container.name][coord],
                    'Spectramax Well': coord
                }

