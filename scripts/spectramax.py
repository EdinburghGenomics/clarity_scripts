#!/usr/bin/env python
from collections import OrderedDict
from logging import FileHandler
from egcg_core.app_logging import logging_default as log_cfg
from EPPs.common import StepEPP, step_argparser


class SpectramaxOutput(StepEPP):
    def __init__(self, step_uri, username, password, log_file, spectramax_file):
        super().__init__(step_uri, username, password, log_file)
        self.spectramax_file = spectramax_file
        self.samples = {}
        self.plates = OrderedDict()
        self.samples_per_plate = None
        self.parse_spectramax_file()

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
                    self.samples[int(split_line[0])] = (split_line[1], split_line[3])

            elif line.startswith('Plate:') and encountered_unknowns:
                self.plates[line.split('\t')[1]] = {}

        self.debug('Found %s samples and %s plates', len(self.samples), len(self.plates))
        self.samples_per_plate = len(self.samples) / len(self.plates)

    def plate_name_for_sample(self, sample_idx):
        plate_idx = 0
        samples_per_plate = self.samples_per_plate
        while sample_idx > samples_per_plate:
            plate_idx += 1
            sample_idx -= samples_per_plate

        return list(self.plates)[int(plate_idx)]

    def _run(self):
        for i, (coord, conc) in self.samples.items():
            plate_name = self.plate_name_for_sample(i)
            self.plates[plate_name][coord] = conc

        self.info('Updating step %s with data: %s' % (self.step_id, self.plates))

        for artifact, (container, coord) in self.process.step.placements.get_placement_list():
            plate_id = container.name
            coord = coord.replace(':', '')
            artifact.udf['Unadjusted Pico Conc (ng/ul)'] = self.plates[plate_id][coord]
            artifact.udf['Spectramax Well'] = coord
            artifact.put()


def main():
    p = step_argparser()
    p.add_argument('--spectramax_file', type=str, required=True, help='Spectramax output file from the step')
    args = p.parse_args()
    log_cfg.add_handler(FileHandler(args.log_file))
    action = SpectramaxOutput(args.step_uri, args.username, args.password, args.log_file, args.spectramax_xml)
    action.run()

if __name__ == '__main__':
    main()
