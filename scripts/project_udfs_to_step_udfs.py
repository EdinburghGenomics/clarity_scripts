#!/usr/bin/env python
import sys
from EPPs.common import StepEPP


class ProjectUDFStepUDF(StepEPP):
    _max_nb_projects = 1
    """
    Pushes and pulls values from step UDF to project UDF.
    """
    def __init__(self, argv=None):
        super().__init__(argv)
        self.project_udfs = self.cmd_args.project_udfs
        self.step_udfs = self.cmd_args.step_udfs
        self.reverse = self.cmd_args.reverse

    @staticmethod
    def add_args(argparser):
        # the -n argument can have as many entries as required, if there are spaces within the udfnames and when running
        # locally, they must be enclosed in speech marks " not quotes ' (-n "udf name 1" "udf name 2") BUT use quotes '
        # when configuring the EPP, as speech marks close the bash command
        argparser.add_argument('-n', '--project_udfs', nargs='*', help='Project UDFs')
        argparser.add_argument('-t', '--step_udfs', nargs='*', help='Step UDFs')
        argparser.add_argument('-r', '--reverse', action='store_true', help='If present sets the script to push from step to project', default=False)

    def _run(self):

            for step_udf, project_udf in zip(self.step_udfs, self.project_udfs):
                if not step_udf in self.process.udf:
                    raise ValueError('Step UDF '+step_udf+' not present')
                elif not project_udf in self.artifacts[0].samples[0].project.udf:
                    raise ValueError('Project UDF ' + project_udf + ' not present')
                else:
                    if self.reverse == False:
                        self.process.udf[step_udf] = self.projects[0].udf[project_udf]

                    if self.reverse == True:
                        self.projects[0].udf[project_udf] = self.process.udf[step_udf]

            if self.reverse == False:
                self.process.put()

            if self.reverse == True:
                self.artifacts[0].samples[0].project.put()


if __name__ == '__main__':
    ProjectUDFStepUDF().run()
