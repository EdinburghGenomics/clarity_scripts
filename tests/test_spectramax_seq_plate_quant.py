from os.path import join, dirname, abspath
from unittest.mock import Mock, patch
from tests.test_common import TestEPP, NamedMock
from scripts.spectramax_seq_plate_quant import SpectramaxOutput


class TestSeqPlateQuantSpectramax(TestEPP):
    exp_concs = {
        1: ('A4', 11.668), 2: ('B4', 12.953), 3: ('C4', 11.956), 4: ('D4', 14.602), 5: ('E4', 15.004)
    }

    exp_concs2 = {
        1: ('A4', 11.668), 2: ('B4', 12.953), 3: ('C4', 11.956), 4: ('D4', 14.602), 5: ('E4', 15.004), 6: ('E4', 15.004)
    }

    exp_plates = {
        'a_plate': {'A4': 11.668, 'B4': 12.953, 'C4': 11.956, 'D4': 14.602, 'E4': 15.004}
    }

    exp_plate_names = ['a_plate']

    def setUp(self):
        self.epp = SpectramaxOutput(
            self.default_argv + [
                '--spectramax_file',
                join(dirname(abspath(__file__)), 'assets', 'kapa_spectramax_output.txt')
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

        #test to see if error raised if badly formed result file with duplicate well
         self.epp.plates.clear()

         self.epp.sample_concs[6]=self.epp.sample_concs[5]

         with self.assertRaises(AssertionError) as e:
             self.epp.assign_samples_to_plates()
         assert str(e.exception) == 'Badly formed spectramax file: tried to add coord E4 for sample 6 to plate a_plate'

    @patch('scripts.spectramax_seq_plate_quant.SpectramaxOutput.process')
    def test_add_plates_to_step(self, mocked_process):
        fake_placements = []
        for plate in self.exp_plate_names:
            for x in 'ABCDEFGH':
                for y in range(4, 13):
                    placement = (Mock(udf={}), (NamedMock(real_name=plate), x + ':' + str(y)))
                    fake_placements.append(placement)

        assert len(fake_placements) == 1 * 72

        self.epp.plates = self.exp_plates.copy()
        mocked_process.step = Mock(placements=Mock(get_placement_list=Mock(return_value=fake_placements)))
        self.epp._add_plates_to_step()

        for artifact, (container, coord) in fake_placements:
            coord = coord.replace(':', '')
            if coord in self.epp.plates[container.name]:
                assert artifact.udf == {
                    'Picogreen Concentration (ng/ul)': self.epp.plates[container.name][coord],
                    'Spectramax Well': coord
                }
                artifact.put.assert_called_once()
