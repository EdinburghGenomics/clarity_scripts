#!/usr/bin/env python
import re
import sys

from EPPs.common import StepEPP


class CheckContainerName(StepEPP):
    """
    Checks that the container name assigned by the user has the correct format for a seqlab plate with the standard
    seqlab prefix "LP[0-9]{7}-" and the suffix specified by an argument.
    """

    def __init__(self, argv=None):
        # extra suffix argument required in addition to standard arg parser arguments
        super().__init__(argv)
        self.suffix = self.cmd_args.suffix

    @staticmethod
    def add_args(argparser):
        argparser.add_argument(
            '-x', '--suffix', type=str, help='Set the suffix of the container name (hyphen present in prefix)'
        )

    def _run(self):
        """
        Assembles the container name template from the fixed prefix and the suffix determined by the argument.
        Find all the output container names and then check that they match the template. If not then sys exit with
        a useful message.
        """
        name_template = "LP[0-9]{7}-" + self.suffix
        containers = self.process.output_containers()

        for container in containers:
            if not re.match(name_template, container.name):
                print("%s is not a valid container name. Container names must match %s" % (container.name, name_template))
                sys.exit(1)


if __name__ == '__main__':
    CheckContainerName().run()
