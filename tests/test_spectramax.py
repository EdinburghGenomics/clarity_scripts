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
        assert list(self.epp.plates) == ['a_plate', 'another_plate', 'yet_another_plate']
        assert self.epp.samples == {
            1: ('A1', 55.107), 2: ('A2', 47.653), 10: ('B1', 43.105), 11: ('B2', 44.311),
            12: ('B3', 43.383), 13: ('A1', 45.566), 14: ('A2', 46.608), 15: ('A3', 44.216),
            16: ('B1', 41.752), 17: ('B2', 44.164), 18: ('B3', 43.852), 3: ('A3', 47.752),
            4: ('B1', 42.683), 5: ('B2', 40.055), 6: ('B3', 43.631), 7: ('A1', 40.211),
            8: ('A2', 41.756), 9: ('A3', 41.704)
        }

    def test_plate_name_for_sample(self):
        assert self.epp.plate_name_for_sample(14) == 'yet_another_plate'

    def test_run(self):
        fake_placements = [
            (Mock(udf={}), (FakeEntity(name='a_plate'), 'A1')),
            (Mock(udf={}), (FakeEntity(name='a_plate'), 'A2')),
            (Mock(udf={}), (FakeEntity(name='a_plate'), 'A3')),
            (Mock(udf={}), (FakeEntity(name='a_plate'), 'B1')),
            (Mock(udf={}), (FakeEntity(name='a_plate'), 'B2')),
            (Mock(udf={}), (FakeEntity(name='a_plate'), 'B3')),
            (Mock(udf={}), (FakeEntity(name='another_plate'), 'A1')),
            (Mock(udf={}), (FakeEntity(name='another_plate'), 'A2')),
            (Mock(udf={}), (FakeEntity(name='another_plate'), 'A3')),
            (Mock(udf={}), (FakeEntity(name='another_plate'), 'B1')),
            (Mock(udf={}), (FakeEntity(name='another_plate'), 'B2')),
            (Mock(udf={}), (FakeEntity(name='another_plate'), 'B3')),
            (Mock(udf={}), (FakeEntity(name='yet_another_plate'), 'A1')),
            (Mock(udf={}), (FakeEntity(name='yet_another_plate'), 'A2')),
            (Mock(udf={}), (FakeEntity(name='yet_another_plate'), 'A3')),
            (Mock(udf={}), (FakeEntity(name='yet_another_plate'), 'B1')),
            (Mock(udf={}), (FakeEntity(name='yet_another_plate'), 'B2')),
            (Mock(udf={}), (FakeEntity(name='yet_another_plate'), 'B3'))
        ]

        self.epp.process = Mock(
            step=Mock(placements=Mock(get_placement_list=Mock(return_value=fake_placements)))
        )

        exp = {
            'a_plate': {
                'A1': 55.107, 'A2': 47.653, 'A3': 47.752, 'B1': 42.683, 'B2': 40.055, 'B3': 43.631
            },
            'another_plate': {
                'A1': 40.211, 'A2': 41.756, 'A3': 41.704, 'B1': 43.105, 'B2': 44.311, 'B3': 43.383
            },
            'yet_another_plate': {
                'A1': 45.566, 'A2': 46.608, 'A3': 44.216, 'B1': 41.752, 'B2': 44.164, 'B3': 43.852
            }
        }

        self.epp._run()
        assert self.epp.plates == exp
        for artifact, (container, coord) in fake_placements:
            assert artifact.udf == {
                'Unadjusted Pico Conc (ng/ul)': exp[container.name][coord],
                'Spectramax Well': coord
            }
            artifact.put.assert_called_once()
