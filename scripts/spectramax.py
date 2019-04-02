#!/usr/bin/env python

from EPPs.common import ParseSpectramaxEPP


class SpectramaxOutput(ParseSpectramaxEPP):
    # define starting well from which "unkowns" will appear in the result file.
    # Standards will not be present in the results table to be parsed
    starting_well = 'A1'

    def _add_plates_to_step(self):
        self.info('Updating step %s with data: %s', self.step_id, self.plates)
        updated_input_artifacts = []

        for artifact, (container, coord) in self.process.step.placements.get_placement_list():
            coord = coord.replace(':', '')
            plate_name = container.name
            if coord not in self.plates[plate_name]:
                self.warning('Could not find coordinate %s for plate %s in spectramax file', coord, plate_name)
                continue

            artifact.udf['Unadjusted Pico Conc (ng/ul)'] = self.plates[plate_name][coord]
            artifact.udf['Spectramax Well'] = coord
            updated_input_artifacts.append(artifact)

        return updated_input_artifacts


if __name__ == '__main__':
    SpectramaxOutput().run()
