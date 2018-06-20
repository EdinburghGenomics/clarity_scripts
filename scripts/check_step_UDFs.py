#!/usr/bin/env python
import sys
from EPPs.common import step_argparser, StepEPP


class CheckStepUDFs(StepEPP):
    """
    Checks Step UDFs have been completed and causes a sys exit if not. Can be prefixed before other python scripts with
    '&&' in EPP.
    """
    def __init__(self, step_uri, username, password, udfnames, log_file=None):
        super().__init__(step_uri, username, password, log_file)
        self.udfnames = udfnames

    def _run(self):
        for udfname in self.udfnames:
            if not self.process.udf.get(udfname):
                print("Please complete step udf '%s'" % udfname)
                sys.exit(1)


def main():
    # Get the default command line options
    p = step_argparser()
    p.add_argument('-n', '--udfnames', nargs='*', help='udfs to be checked if completed')
    # the -n argument can have as many entries as required, if there are spaces within the udfnames and when running
    # locally, they must be enclosed in speech marks " not quotes ' (-n "udf name 1" "udf name 2") BUT use quotes ' when
    # configuring the EPP as speech marks close the bash command

    # Parse command line options
    args = p.parse_args()

    # Setup the EPP
    action = CheckStepUDFs(
        args.step_uri, args.username, args.password, args.udfnames, args.log_file,
    )

    # Run the EPP
    action.run()


if __name__ == '__main__':
    main()
