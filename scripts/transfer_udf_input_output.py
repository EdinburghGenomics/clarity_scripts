#!/usr/bin/env python
from EPPs.common import StepEPP


class TransferUDFInputOutput(StepEPP):
    #transfers input udf value to all child output analyte udfs. udf is specified by an argument

    def __init__(self, argv=None):
        super().__init__(argv)
        self.udfnames = self.cmd_args.udfnames

    @staticmethod
    def add_args(argparser):
        # the -n argument can have as many entries as required, if there are spaces within the udfnames and when running
        # locally, they must be enclosed in speech marks " not quotes ' (-n "udf name 1" "udf name 2") BUT use quotes '
        # when configuring the EPP, as speech marks close the bash command
        argparser.add_argument('-n', '--udfnames', nargs='*', help='UDFs to be checked if completed')

    def _run(self):
        for artifact in self.artifacts:

            outputs=self.process.outputs_per_input(artifact.id, Analyte=True)
            for output in outputs:
                for udfname in self.udfnames:
                    output.udf[udfname]=artifact.udf[udfname]
                output.put()

if __name__=='__main__':
    TransferUDFInputOutput().run()