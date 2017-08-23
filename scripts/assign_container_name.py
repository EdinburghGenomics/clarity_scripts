#!/usr/bin/env python
from EPPs.common import StepEPP, step_argparser, get_workflow_stage


class AssignContainerName(StepEPP):

    def nameContainer(self, projectName):
        artifacts = self.process.all_outputs(unique=True)
        artifacts[0].container.name = projectName
        artifacts[0].container.name.put()



    def _run(self):
        projects = self.projects(unique=True)
        projectName=projects[0].name
        print(projectName)
        nameContainer(projectName)




def main():
    p = step_argparser()
    args = p.parse_args()
    action = AssignContainerName(args.step_uri, args.username, args.password)
    action.run()
    action.run()


if __name__ == '__main__':
    main()
