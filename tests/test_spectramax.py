from os.path import join, dirname, abspath
from unittest.mock import Mock
from tests.test_common import TestEPP, FakeEntity
from scripts import spectramax


class TestSpectramaxOutput(TestEPP):
    def setUp(self):
        self.epp = spectramax.SpectramaxOutput(
            'http://server:8080/a_step_uri',
            'a_user',
            'a_password',
            'a_log_file',
            join(dirname(abspath(__file__)), 'assets', 'spectramax_output.txt')
        )

    def test_parse_spectramax_file(self):
        assert list(self.epp.plate_names) == ['a_plate', 'another_plate', 'yet_another_plate']
        assert self.epp.sample_concs == {
            1: ('A1', 55.107), 2: ('A2', 47.653), 9: ('B1', 43.105), 10: ('B2', 44.311), 11: ('B3', 43.383),
            12: ('A1', 45.566), 13: ('A2', 46.608), 14: ('A3', 44.216), 15: ('B1', 41.752), 3: ('A3', 47.752),
            4: ('B1', 42.683), 5: ('B2', 40.055), 6: ('A1', 40.211), 7: ('A2', 41.756), 8: ('A3', 41.704)
        }

    def test_run(self):
        fake_placements = []
        for plate in ('a_plate', 'another_plate', 'yet_another_plate'):
            for x in 'ABCDEFGH':
                for y in range(1, 13):
                    placement = (Mock(udf={}), (FakeEntity(name=plate), x + ':' + str(y)))
                    fake_placements.append(placement)

        assert len(fake_placements) == 3 * 96

        self.epp.process = Mock(
            step=Mock(placements=Mock(get_placement_list=Mock(return_value=fake_placements)))
        )

        exp = {
            'a_plate': {
                'A1': 55.107, 'A2': 47.653, 'A3': 47.752, 'B1': 42.683, 'B2': 40.055
            },
            'another_plate': {
                'A1': 40.211, 'A2': 41.756, 'A3': 41.704, 'B1': 43.105, 'B2': 44.311, 'B3': 43.383
            },
            'yet_another_plate': {
                'A1': 45.566, 'A2': 46.608, 'A3': 44.216, 'B1': 41.752
            }
        }

        self.epp._run()
        assert self.epp.plates == exp
        for artifact, (container, coord) in fake_placements:
            coord = coord.replace(':', '')
            if coord in exp[container.name]:
                assert artifact.udf == {
                    'Unadjusted Pico Conc (ng/ul)': exp[container.name][coord],
                    'Spectramax Well': coord
                }
                artifact.put.assert_called_once()
