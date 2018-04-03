#!/usr/bin/env python
from EPPs.common import StepEPP, step_argparser


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
                new_container_name = self.find_available_container(project)
                p.container.name = new_container_name
                p.container.put()

                break

    def find_available_container(self, project, count=1):
        """
        Check to see if a container name is available, and recurse with incremented container numbers until an available
        container name is found.
        :param str project:
        :param int count:
        """
        if count > 999:
            raise ValueError('Cannot allocate more than 999 containers')

        new_name = project + 'P%03d' % count

        if not self.lims.get_artifacts(containername=new_name):
            return new_name
        else:
            return self.find_available_container(project, count=count + 1)


def main():
    p = step_argparser()
    args = p.parse_args()
    action = AssignContainerName(args.step_uri, args.username, args.password)
    action.run()


if __name__ == '__main__':
    main()
