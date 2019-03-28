#!/usr/bin/env python
from EPPs.common import StepEPP
from pyclarity_lims.entities import Protocol


class CheckStepUDF(StepEPP):
    """
    Checks if steps specified in arguments have their default value or not
    """
    def __init__(self, argv=None):
        super().__init__(argv)
        self.check_udfs = self.cmd_args.check_udfs
        self.default_values = self.cmd_args.default_values

    @staticmethod
    def add_args(argparser):
        argparser.add_argument('-c', '--check_udfs', nargs='*',help='Select the step udf for checking')
        argparser.add_argument('-d', '--default_values', nargs='*',help='Default value for each step udf')

    def _run(self):
        for check_udf, default_value in \
                zip(self.check_udfs, self.default_values):
            print(check_udf,default_value)
            if self.process.udf[check_udf]==default_value:
                raise ValueError('Please complete '+check_udf)

if __name__ == '__main__':
    CheckStepUDF().run()
