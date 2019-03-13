#!/usr/bin/env python
from EPPs.common import StepEPP


class AssignContainerName(StepEPP):
    """
    Assigns a container name for, e.g, the FluidX Transfer from Rack to Plate step in the format
    '{project_id}P{number}. Automatically checks previously used container names to ensure a new name is used.
    """

    def _run(self):
        """
        Update each analyte-type artifact with a new, unused container name. This only needs to occur once as the step
        can only process a single rack of tubes from a single project.
        """
        for p in list(self.process.all_outputs(unique=True)):
            if p.output_type == 'Analyte':
               
                project = p.samples[0].project.name
                new_container_name = self.find_available_container(project, '96 well plate')
                p.container.name = new_container_name
                p.container.put()

                break


if __name__ == '__main__':
    AssignContainerName().run()
