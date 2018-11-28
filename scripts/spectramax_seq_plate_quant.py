#!/usr/bin/env python

from EPPs.common import ParseSpectramaxEPP


class SpectramaxOutput(ParseSpectramaxEPP):
    _use_load_config = False  # prevent the loading of the config

    # define starting well from which "unkowns" will appear in the result file. Standards will not be present in the results table to be parsed
    starting_well = 'A4'

    def _add_plates_to_step(self):

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

        # Average replicates. For the normal usage of this script there will be 3 output replicates for each input.
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

        return input_artifacts_replicates


if __name__ == '__main__':
    SpectramaxOutput().run()
