#!/usr/bin/env python
from EPPs.common import StepEPP, step_argparser, get_workflow_stage


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
                newContainerName = FindAvailableContainer(self, project=project, count=1, zeros='00')
                p.container.name = newContainerName
                p.container.put()

                break




def FindAvailableContainer(self, project, count, zeros):
    # checks to see if the first container name is available and then recurses until it finds an available container name
    if self.lims.get_artifacts(containername=project + 'P' + zeros + str(count)) == []:
        newContainerName = project + 'P' + zeros + str(count)
        return newContainerName
    else:
        count = count + 1
        if count > 9 and count < 100:  # the plate naming convention has the number -count- preceeded by zeros to make up three digits e.g. 001, 010
            zeros = '0'
        elif count > 99:
            zeros = ''

        newContainerName = FindAvailableContainer(self, project=project, count=count, zeros=zeros)

        return newContainerName


def main():
    p = step_argparser()
    args = p.parse_args()
    action = AssignContainerName(args.step_uri, args.username, args.password)
    action.run()


if __name__ == '__main__':
    main()