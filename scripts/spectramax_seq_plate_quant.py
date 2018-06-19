#!/usr/bin/env python
from collections import defaultdict
from logging import FileHandler
from egcg_core.app_logging import logging_default as log_cfg
from EPPs.common import StepEPP, step_argparser
import sys


class SpectramaxOutput(StepEPP):
    def __init__(self, step_uri, username, password, log_file, spectramax_file):
        super().__init__(step_uri, username, password, log_file)
        self.spectramax_file = spectramax_file
        self.sample_concs = {}
        self.plate_names = []
        self.plates = defaultdict(dict)

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
            if coord == 'A1':  # ... and take an 'A1' coord as the start of a new plate
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

        for artifact, (container, coord) in self.process.step.placements.get_placement_list():
            coord = coord.replace(':', '')
            plate_name = container.name
            if coord not in self.plates[plate_name]:
                self.warning('Could not find coordinate %s for plate %s in spectramax file', coord, plate_name)
                continue

            artifact.udf['Picogreen Concentration (ng/ul)'] = self.plates[plate_name][coord]
            artifact.udf['Spectramax Well'] = coord
            artifact.put()



    def average_replicates(self):
        input_artifacts_replicates={}
        input_mean={}

        for input_output_map in self.process.input_output_maps:
            if input_output_map[0]['uri'] in input_artifacts_replicates.keys() and input_output_map[1]['output-generation-type']=='PerInput':

                input_artifacts_replicates[input_output_map[0]['uri']].append(input_output_map[1]['uri'].udf.get('Picogreen Concentration (ng/ul)'))
            elif input_output_map[0]['uri'] not in input_artifacts_replicates.keys() and input_output_map[1]['output-generation-type']=='PerInput':

                input_artifacts_replicates[input_output_map[0]['uri']]=[input_output_map[1]['uri'].udf.get('Picogreen Concentration (ng/ul)')]


        for input_artifact in input_artifacts_replicates:
            total = 0
            for replicate in input_artifacts_replicates[input_artifact]:
                total = total+replicate
            input_artifact.udf['Picogreen Concentration (ng/ul)']=total/len(input_artifacts_replicates[input_artifact])

        self.lims.put_batch(list(input_artifacts_replicates))





    def _run(self):
        self.parse_spectramax_file()
        self.assign_samples_to_plates()
        self.add_plates_to_step()
        self.average_replicates()


def main():
    p = step_argparser()
    p.add_argument('--spectramax_file', type=str, required=True, help='Spectramax output file from the step')
    args = p.parse_args()
    log_cfg.add_handler(FileHandler(args.log_file))
    action = SpectramaxOutput(args.step_uri, args.username, args.password, args.log_file, args.spectramax_file)
    action.run()

if __name__ == '__main__':
    main()
