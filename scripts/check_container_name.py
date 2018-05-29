#!/usr/bin/env python
import re
import sys

from EPPs.common import StepEPP, step_argparser


class CheckContainerName(StepEPP):
    """
    Checks that the container name assigned by the user has the correct format for a seqlab plate with the standard
    seqlab prefix "LP[0-9]{7}-" and the suffix specified by an argument.
    """

    def __init__(self, step_uri, username, password, suffix):
        #extra suffix argument required in addition to standard arg parser arguments
        super().__init__(step_uri, username, password)
        self.suffix = suffix

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
                print("%s is not a valid container name. Container names must match %s" % (container, name_template))
                sys.exit(1)


def main():
    p = step_argparser()
    p.add_argument('-x', '--suffix', type=str, help='set the suffix of the container name (hyphen present in prefix)')
    args = p.parse_args()

    action = CheckContainerName(args.step_uri, args.username, args.password, args.suffix)
    action.run()


if __name__ == '__main__':
    main()
