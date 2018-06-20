#!/usr/bin/env python
import sys
from EPPs.common import StepEPP


class CheckStepUDFs(StepEPP):
    """
    Checks Step UDFs have been completed and causes a sys exit if not. Can be prefixed before other python scripts with
    '&&' in EPP.
    """
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
        for udfname in self.udfnames:
            if not self.process.udf.get(udfname):
                print("Please complete step udf '%s'" % udfname)
                sys.exit(1)


if __name__ == '__main__':
    CheckStepUDFs().run()
