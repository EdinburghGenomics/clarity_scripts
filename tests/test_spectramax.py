from os.path import join, dirname, abspath
from unittest.mock import Mock
from tests.test_common import TestEPP, FakeEntity
from scripts import spectramax


class TestSpectramaxOutput(TestEPP):
    expected_data = {
        'a_plate-QNT': {
            'A1': '1500.0', 'A2': '1500.1', 'A3': '1500.2', 'B1': '1500.3', 'B2': '1500.4', 'B3': '1500.5',
            'C1': '1500.6', 'C2': '1500.7', 'C3': '1500.8'
        },
        'another_plate-QNT': {
            'A1': '1600.0', 'A2': '1600.1', 'A3': '1600.2', 'B1': '1600.3', 'B2': '1600.4', 'B3': '1600.5',
            'C1': '1600.6', 'C2': '1600.7', 'C3': '1600.8'
        }
    }

    def setUp(self):
        self.epp = spectramax.SpectramaxOutput(
            'http://server:8080/a_step_uri',
            'a_user',
            'a_password',
            'a_log_file',
            join(dirname(abspath(__file__)), 'assets', 'spectramax_output.xml')
        )

    def test_plates(self):
        assert sorted(e.attrib['Name'] for e in self.epp.plates) == [
            'a_plate-QNT', 'another_plate-QNT', 'standards-SQNT'
        ]

    def test_get_plate(self):
        assert self.epp.get_plate('a_plate-QNT').attrib['Name'] == 'a_plate-QNT'

    def test_coordinate_map(self):
        assert self.epp.coordinate_map(self.epp.get_plate('a_plate-QNT')) == self.expected_data['a_plate-QNT']
        assert self.epp.coordinate_map(self.epp.get_plate('another_plate-QNT')) == self.expected_data['another_plate-QNT']

    def test_run(self):
        fake_placements = [
            (Mock(udf={}), (FakeEntity(name='a_plate-QNT'), 'A1')),
            (Mock(udf={}), (FakeEntity(name='a_plate-QNT'), 'A2')),
            (Mock(udf={}), (FakeEntity(name='a_plate-QNT'), 'A3')),
            (Mock(udf={}), (FakeEntity(name='a_plate-QNT'), 'B1')),
            (Mock(udf={}), (FakeEntity(name='a_plate-QNT'), 'B2')),
            (Mock(udf={}), (FakeEntity(name='a_plate-QNT'), 'B3')),
            (Mock(udf={}), (FakeEntity(name='a_plate-QNT'), 'C1')),
            (Mock(udf={}), (FakeEntity(name='a_plate-QNT'), 'C2')),
            (Mock(udf={}), (FakeEntity(name='a_plate-QNT'), 'C3')),
            (Mock(udf={}), (FakeEntity(name='another_plate-QNT'), 'A1')),
            (Mock(udf={}), (FakeEntity(name='another_plate-QNT'), 'A2')),
            (Mock(udf={}), (FakeEntity(name='another_plate-QNT'), 'A3')),
            (Mock(udf={}), (FakeEntity(name='another_plate-QNT'), 'B1')),
            (Mock(udf={}), (FakeEntity(name='another_plate-QNT'), 'B2')),
            (Mock(udf={}), (FakeEntity(name='another_plate-QNT'), 'B3')),
            (Mock(udf={}), (FakeEntity(name='another_plate-QNT'), 'C1')),
            (Mock(udf={}), (FakeEntity(name='another_plate-QNT'), 'C2')),
            (Mock(udf={}), (FakeEntity(name='another_plate-QNT'), 'C3'))
        ]

        self.epp.process = Mock(
            step=Mock(
                placements=Mock(
                    get_placement_list=Mock(return_value=fake_placements),
                    get_selected_containers=Mock(
                        return_value=[FakeEntity(name='a_plate-QNT'), FakeEntity(name='another_plate-QNT')]
                    )
                )
            )
        )

        self.epp._run()
        for artifact, (container, coord) in fake_placements:
            assert artifact.udf == {
                'Unadjusted Pico Conc (ng/ul)': self.expected_data[container.name][coord],
                'Spectramax Well': coord
            }
            artifact.put.assert_called_once()
