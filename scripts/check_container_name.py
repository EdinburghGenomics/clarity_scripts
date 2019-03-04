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
    _use_load_config = False  # prevent the loading of the config file
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
        Check to see if the names of the containers in the step match any of the allowed name formats which are defined by the fixed name_template
        prefix and a number of suffixes supplied by suffix argument.
        """
        containers = self.process.output_containers()

        suffixes = self.suffix


        for container in containers:
            valid_container=False
            for suffix in suffixes:
                name_template = 'LP[0-9]{7}-' + suffix
                if re.match(name_template, container.name):
                    valid_container=True
            if valid_container==False:
                raise InvalidStepError("Container name %s is not valid for the step. Expected name format is prefix 'LP[0-9]{7}-' with one of the following suffixes: %s." %(container.name, suffixes))



if __name__ == '__main__':
    CheckContainerName().run()
