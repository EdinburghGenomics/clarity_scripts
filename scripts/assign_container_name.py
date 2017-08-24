#!/opt/gls/clarity/users/glsai/Applications/clarity_scripts/import_prod_script/bin/python3.4
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
                print(p)
                project = p.samples[0].project.name
                newContainerName = FindAvailableContainer(self, project=project, count=1)
                p.container.name = newContainerName
                p.container.put()

                break

        print(newContainerName)


def FindAvailableContainer(self, project, count):
    if self.lims.get_artifacts(containername=project + 'P' + str(count)) == []:
        newContainerName = project + 'P' + str(count)
        return newContainerName
    else:
        count = count + 1
        print(self.lims.get_artifacts(containername=project + 'P' + str(count)) == [])
        newContainerName = FindAvailableContainer(self, project=project, count=count)

        return newContainerName


def main():
    p = step_argparser()
    args = p.parse_args()
    action = AssignContainerName(args.step_uri, args.username, args.password)
    action.run()


if __name__ == '__main__':
    main()