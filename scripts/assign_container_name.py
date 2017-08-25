#!/usr/bin/env python
from EPPs.common import StepEPP, step_argparser


class AssignContainerName(StepEPP):
    # assigns the container automatically for the FluidX Transfer from Rack to Plate step using rule of Project+P+9.
    # Checks to see if thecontainer name has already been used.

    def _run(self):
        # lists all of the output artifacts for the process.
        processOutputs = list(self.process.all_outputs(unique=True))

        # loops through each artifact, when an analyte type artifact is found it updates the container name with the rule stated above then breaks the loop
        # as this only needs to occur once as the step can only process a single rack of tubes from a single project.
        for p in processOutputs:
            if p.output_type == 'Analyte':
               
                project = p.samples[0].project.name
                new_container_name = self.findAvailableContainer(project=project, count=1)
                p.container.name = new_container_name
                p.container.put()

                break




    def findAvailableContainer(self, project, count):
        # checks to see if the first container name is available and then recurses until it finds an available container name

        if count>999:
            raise ValueError('Cannot allocate more than 999 containers')

        new_name=project+'P%03d' % (count)

        if self.lims.get_artifacts(containername=project + 'P' + zeros + str(count)) == []:
            return new_name
        else:
            return self.findAvailableContainer(project=project, count=count+1)



def main():
    p = step_argparser()
    args = p.parse_args()
    action = AssignContainerName(args.step_uri, args.username, args.password)
    action.run()


if __name__ == '__main__':
    main()