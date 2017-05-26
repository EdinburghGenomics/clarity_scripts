import xml.etree.ElementTree as ETree
from collections import defaultdict
from cached_property import cached_property
from EPPs.common import StepEPP, step_argparser


class SpectramaxOutput(StepEPP):
    def __init__(self, step_uri, username, password, log_file, spectramax_xml):
        super().__init__(step_uri, username, password, log_file)
        self.spectramax_xml = spectramax_xml

    @cached_property
    def plates(self):
        root = ETree.parse(self.spectramax_xml)
        return root.findall('PlateSections/PlateSection')

    def get_plate(self, plate_id):
        plates = [p for p in self.plates if p.attrib['Name'] == plate_id]
        assert len(plates) == 1, '%s -> %s' % (plate_id, plates)
        return plates[0]

    @staticmethod
    def coordinate_map(plate):
        wells = plate.findall('reducedData/Well')
        return {w.attrib['Name']: w.find('reducedVal').text for w in wells}

    def _run(self):
        output_data = defaultdict(dict)
        for container in self.process.step.placements.get_selected_containers():
            plate_id = container.name
            output_data[plate_id] = self.coordinate_map(self.get_plate(plate_id))
        print(output_data)

        for artifact, (container, coord) in self.process.step.placements.get_placement_list():
            plate_id = container.name
            coord = coord.replace(':', '')
            print(
                "%s: artifact.udf.update({'Unadjusted Pico Conc (ng/ul)': '%s', 'Spectramax Well': '%s'})" % (
                    artifact.name, output_data[plate_id][coord], coord
                )
            )


def main():
    p = step_argparser()
    p.add_argument('--spectramax_xml', type=str, required=True, help='The Spectramax XML output file from the step')
    args = p.parse_args()
    action = SpectramaxOutput(args.step_uri, args.username, args.password, args.log_file, args.spectramax_xml)
    action.run()
