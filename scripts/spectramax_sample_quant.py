#!/usr/bin/env python

from EPPs.common import ParseSpectramaxEPP


class SpectramaxOutput(ParseSpectramaxEPP):
    # define starting well from which "unkowns" will appear in the result file.
    # Standards will not be present in the results table to be parsed
    starting_well = 'A1'


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
                    self.sample_concs[int(split_line[0])] = (split_line[1], float(split_line[2]))

            elif line.startswith('Plate:') and encountered_unknowns:
                self.plate_names.append(line.split('\t')[1])
        if self.sample_concs[1][0] != self.starting_well:
            raise AssertionError(
                'Badly formed spectramax file: first well for samples is %s but expected to be %s'
                % (str(self.sample_concs[1][0]),str(self.starting_well))
            )

        self.debug('Found %s samples and %s plates', len(self.sample_concs), len(self.plate_names))

    def _add_plates_to_step(self):
        self.info('Updating step %s with data: %s', self.step_id, self.plates)
        updated_input_artifacts = []

        for artifact, (container, coord) in self.process.step.placements.get_placement_list():
            coord = coord.replace(':', '')
            plate_name = container.name
            if coord not in self.plates[plate_name]:
                self.warning('Could not find coordinate %s for plate %s in spectramax file', coord, plate_name)
                continue

            artifact.udf['Raw Value'] = self.plates[plate_name][coord]
            updated_input_artifacts.append(artifact)

        return updated_input_artifacts


if __name__ == '__main__':
    SpectramaxOutput().run()
