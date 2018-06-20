#!/usr/bin/env python
from EPPs.common import StepEPP
from pyclarity_lims.entities import Protocol


class AssignNextStep(StepEPP):
    """
    This script assigns the next step for all samples in the step as either "review", "complete" or "nextstep"
    for next step it assumes the next step wanted is the next step in the protocol i.e. doesn't skip one or more steps
    in the configuration assumes that all artifacts should have the same next step
    """
    def __init__(self, argv=None):
        super().__init__(argv)
        self.review = self.cmd_args.review
        self.remove = self.cmd_args.remove

    @staticmethod
    def add_args(argparser):
        argparser.add_argument('-r', '--review', action='store_true', help='Set the next step to review', default=False)
        argparser.add_argument('-e', '--remove', action='store_true', help='Set the next step to remove', default=False)

    def _run(self):

        # obtain the actions of the step then creates a StepActions entity for the current step
        actions = self.process.step.actions

        # obtain the next actions in the step then creates a list of dict for next_actions for the step
        next_actions = actions.next_actions

        # check to see if review argument flag is present, if 'true' then set all next actions to "review"
        if self.review:
            # for all artifacts in next_actions update the action to "review"
            for next_action in next_actions:
                next_action['action'] = 'review'

        elif self.remove:
            # for all artifacts in the next_actions update the action to "remove"
            for next_action in next_actions:
                next_action['action'] = 'remove'

        # If review argument flag is not present then either nextstep or complete are the options
        else:
            current_step = self.process.step.configuration  # configuration gives the ProtocolStep entity.
            protocol = Protocol(self.process.lims, uri='/'.join(self.process.step.configuration.uri.split('/')[:-2]))
            steps = protocol.steps  # a list of all the ProtocolSteps in protocol
            # If the step is the last step in the protocol then set the next action to complete
            if current_step == steps[-1]:
                # for all artifacts in next_actions update the action to "complete"
                for next_action in next_actions:
                    next_action['action'] = 'complete'

            # If the step is not the last step in the protocol then set the next action to the next step
            # and assign the identity of that step with the step_object
            else:
                step_object = steps[steps.index(current_step) + 1]
                # for all artifacts in next_actions update the action to "next step" with the step
                # as the next step in the protocol
                for next_action in next_actions:
                    next_action['action'] = 'nextstep'
                    next_action['step'] = step_object

        actions.put()


if __name__ == '__main__':
    AssignNextStep().run()
