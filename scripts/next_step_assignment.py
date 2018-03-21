#!/usr/bin/env python
from EPPs.common import step_argparser, StepEPP
from EPPs.config import load_config
# from pyclarity_lims.entities import ProtocolStep
from pyclarity_lims.entities import Protocol


class AssignNextStep(
    StepEPP):  # finds the next step in the protocol and assigns it to the artifacts appearing in the Next Steps of the script -
    # assumes the next step wanted is the next step in the protocol i.e. doesn't skip one or more steps in the configuration
    # assumes that all artifacts should have the same next step
    def __init__(self, step_uri, username, password, log_file=None, review=False):
        super().__init__(step_uri, username, password, log_file)
        self.review = review

    def _run(self):

        actions = self.process.step.actions  # obtain the actions of the step # creates a StepActions entity for the current step

        next_actions = actions.next_actions  # obtain the next actions in the step #creates a list of dict for next_actions for the step

        if self.review==True:
            for next_action in next_actions:  # for all artifacts in next_actions update the action to "complete" with the step as the next step in the protocol
                next_action['action'] = 'review'

            actions.put()

        elif self.review==False:
            current_step = self.process.step.configuration  # configuration gives the ProtocolStep entity.

            protocol = Protocol(self.process.lims, uri='/'.join(self.process.step.configuration.uri.split('/')[:-2]))



            steps = protocol.steps  # a list of all the ProtocolSteps in protocol


            #for step in steps:  # find the index of the current step in the list of all ProtocolSteps
            #    if step == current_step:
            #        current_step_index = steps.index(step)

            # if the current step index plus 1 matches the number of steps in the protocol (i.e. length of the steps list) then the current step must be the last step in
            # the protocol so the next action should be complete. If the current step index plus 1 is less than the length then next action should be next step

            #if current_step_index + 1 == len(steps):  # where index values run 0 to X and length values run 1 to X
            if current_step==steps[-1]:
                for next_action in next_actions:  # for all artifacts in next_actions update the action to "complete" with the step as the next step in the protocol
                    next_action['action'] = 'complete'

            #elif current_step_index + 1 < len(steps):  # where index values run 0 to X and length values run 1 to X
            else:
                step_object = steps[steps.index(current_step) + 1]
                for next_action in next_actions:  # for all artifacts in next_actions update the action to "next step" with the step as the next step in the protocol
                    next_action['action'] = 'nextstep'
                    next_action['step'] = step_object

            actions.put()


def main():
    # Get the default command line options
    p = step_argparser()
    p.add_argument('-r', '--review', action='store_true', help='set the next step to review', default=False)
    # Parse command line options
    args = p.parse_args()

    # Load the config from the default location
    load_config()

    # Setup the EPP
    action = AssignNextStep(
        args.step_uri, args.username, args.password, args.log_file, args.review
    )

    # Run the EPP
    action.run()


if __name__ == "__main__":
    main()