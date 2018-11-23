#!/usr/bin/env python
import re

from EPPs.common import StepEPP, InvalidStepError


class CheckContainerName(StepEPP):
    """
    Checks that the container name(s) assigned by the user has the correct format for a seqlab plate with the standard
    seqlab prefix "LP[0-9]{7}-" and the suffix(es) specified by an argument. The number of suffixes is no limited but
    script assumes that each suffix is only used once and that the suffixes are applied to the output containers in
    the same order as they appear in the suffix argument
    """

    def __init__(self, argv=None):
        # extra suffix argument required in addition to standard arg parser arguments
        super().__init__(argv)
        self.suffix = self.cmd_args.suffix

    @staticmethod
    def add_args(argparser):
        argparser.add_argument(
            '-x', '--suffix', nargs='*',
            help='Set the suffix of the container name(s) in order plates should appear'
        )

    def _run(self):
        """
        Assemble the container name template from the fixed prefix and the suffix determined by self.suffix. Find all
        the output container names and then check that they match the template. If not, then sys.exit with a useful
        message.
        """
        containers = self.process.output_containers()

        suffixes = self.suffix
        #suffixes.append(self.suffix)
        if len(suffixes) != len(containers):
            raise InvalidStepError(
                message="The number of plate name suffixes must match the number of output containers. %s plate"
                        "name suffixes configured for this step and %s output containers present. The expected suffixes are %s."
                        % (str(len(suffixes)), str(len(containers)), str(suffixes)))

        suffix_counter = 0

        for suffix in suffixes:
            name_template = 'LP[0-9]{7}-' + suffix

            if not re.match(name_template, containers[suffix_counter].name):
                raise InvalidStepError(
                    message="Expected container name format %s does not match container name %s. Please note that"
                            ", if more than one container, the order of suffixes %s must match the order of containers." % (name_template, containers[suffix_counter].name, suffixes))
            suffix_counter+=1

if __name__ == '__main__':
    CheckContainerName().run()
