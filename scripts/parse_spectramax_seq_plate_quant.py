#!/usr/bin/env python
from collections import defaultdict

from EPPs.common import StepEPP


class SpectramaxOutput(StepEPP):
    _use_load_config = False  # prevent the loading of the config

    def __init__(self, argv=None):
        super().__init__(argv)
        self.spectramax_file = self.cmd_args.spectramax_file
        self.sample_concs = {}
        self.plate_names = []
        self.plates = defaultdict(dict)

    @staticmethod
    def add_args(argparser):
        argparser.add_argument('--spectramax_file', type=str, required=True,
                               help='Spectramax output file from the step')

    def parse_spectramax_file(self):
        f = self.open_or_download_file(self.spectramax_file, encoding='utf-16', crlf=True)
        encountered_unknowns = False
        in_unknowns = False

        for line in f:
            if line.startswith('Group: Unknowns'):
                assert not in_unknowns
                in_unknowns = True
                encountered_unknowns = True

            elif line.startswith('~End'):
                in_unknowns = False

            elif in_unknowns:
                if line.startswith('Sample') or line.startswith('Group Summaries'):
                    pass
                else:

                    split_line = line.split('\t')
                    self.sample_concs[int(split_line[0])] = (split_line[1], float(split_line[3]))

            elif line.startswith('Plate:') and encountered_unknowns:
                self.plate_names.append(line.split('\t')[1])

        self.debug('Found %s samples and %s plates', len(self.sample_concs), len(self.plate_names))

    def assign_samples_to_plates(self):
        plate_idx = -1
        plate_name = None
        for i in sorted(self.sample_concs):  # go through in ascending order...
            coord, conc = self.sample_concs[i]
            if coord == 'A4':  # ... and take an 'A1' coord as the start of a new plate
                plate_idx += 1
                plate_name = self.plate_names[plate_idx]

            if coord in self.plates[plate_name]:
                raise AssertionError(
                    'Badly formed spectramax file: tried to add coord %s for sample %s to plate %s' % (
                        coord, i, plate_name
                    )
                )
            self.plates[plate_name][coord] = conc

    def add_plates_to_step(self):
        self.info('Updating step %s with data: %s', self.step_id, self.plates)

        # create list of well positions used by standards so this can be ignored by check for missing sample
        # data
        standards_wells = []
        column_list = ['1', '2', '3']
        row_list = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']

        for column in column_list:
            for row in row_list:
                standards_wells.append(row + str(column))

        for artifact, (container, coord) in self.process.step.placements.get_placement_list():
            coord = coord.replace(':', '')
            plate_name = container.name

            # check if data for sample in step is present in the list of data. Ignore standards.

            if coord not in self.plates[plate_name] and coord not in standards_wells:
                print('Could not find coordinate %s for plate %s in spectramax file' % (coord, plate_name))
                continue

            elif coord not in standards_wells and coord in self.plates[plate_name]:
                artifact.udf['Picogreen Concentration (ng/ul)'] = self.plates[plate_name][coord]
                artifact.udf['Spectramax Well'] = coord
                artifact.put()

    def average_replicates(self):
        # ignores standards as no concentration data generated for these
        input_artifacts_replicates = {}

        for input_output_map in self.process.input_output_maps:
            if not input_output_map[0]['uri'].name.split(' ')[0] == 'SDNA':
                if input_output_map[0]['uri'] in input_artifacts_replicates.keys() and input_output_map[1][
                    'output-generation-type'] == 'PerInput':

                    input_artifacts_replicates[input_output_map[0]['uri']].append(
                        input_output_map[1]['uri'].udf.get('Picogreen Concentration (ng/ul)'))
                elif input_output_map[0]['uri'] not in input_artifacts_replicates.keys() and input_output_map[1][
                    'output-generation-type'] == 'PerInput':

                    input_artifacts_replicates[input_output_map[0]['uri']] = [
                        input_output_map[1]['uri'].udf.get('Picogreen Concentration (ng/ul)')]

        for input_artifact in input_artifacts_replicates:
            total = 0
            for replicate in input_artifacts_replicates[input_artifact]:
                total = total + replicate
            input_artifact.udf['Picogreen Concentration (ng/ul)'] = total / len(
                input_artifacts_replicates[input_artifact])

        self.lims.put_batch(list(input_artifacts_replicates))

    def _run(self):
        self.parse_spectramax_file()
        self.assign_samples_to_plates()
        self.add_plates_to_step()
        self.average_replicates()


if __name__ == '__main__':
    SpectramaxOutput().run()
