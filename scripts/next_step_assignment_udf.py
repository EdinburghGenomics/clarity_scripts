#!/usr/bin/env python
from EPPs.common import StepEPP
from pyclarity_lims.entities import Protocol


class AssignNextStepCreateManifest(StepEPP):
    """
    Assigns next step based on UDF value
    """

    def __init__(self, argv=None):
        super().__init__(argv)
        self.step_udf = self.cmd_args.step_udf
        self.udf_values = self.cmd_args.udf_values
        self.next_steps = self.cmd_args.next_steps



    @staticmethod
    def add_args(argparser):
        argparser.add_argument('-f', '--step_udf', type=str, help='Step UDF to be checked')
        argparser.add_argument('-v', '--udf_values', nargs='*', help='Value in UDF')
        argparser.add_argument('-n', '--next_steps', nargs='*', help='Next step corresponding to value')

    def _run(self):

        current_step = self.process.step.configuration  # configuration gives the ProtocolStep entity.
        protocol = Protocol(self.process.lims,
                            uri='/'.join(self.process.step.configuration.uri.split('/')[:-2]))
        steps = protocol.steps  # a list of all the ProtocolSteps in protocol

        for udf_value, next_step in zip(self.udf_values, self.next_steps):
            if not self.step_udf in self.process.udf:
                raise ValueError('Step UDF ' + self.step_udf + ' not present')

            else:

                if self.process.udf[self.step_udf] == udf_value:

                    for step in steps:
                        if step.name == next_step:

                            next_step_object=step


                else:

                    step_object = steps[steps.index(current_step) + 1]
                    # for all artifacts in next_actions update the action to "next step" with the step
                    # as the next step in the protocol

                    next_step_object = step_object

        # obtain the actions of the step then creates a StepActions entity for the current step
        actions = self.process.step.actions

        # obtain the next actions in the step then creates a list of dict for next_actions for the step
        next_actions = actions.next_actions


        for next_action in next_actions:
            next_action['action'] = 'nextstep'
            next_action['step'] = next_step_object

        actions.put()


if __name__ == '__main__':
    AssignNextStepCreateManifest().run()
