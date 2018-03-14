#!/usr/bin/env python
from EPPs.common import step_argparser, StepEPP
from EPPs.config import load_config
# from pyclarity_lims.entities import ProtocolStep
from pyclarity_lims.entities import Protocol


class AssignNextStep(
    StepEPP):  # finds the next step in the protocol and assigns it to the artifacts appearing in the Next Steps of the script -
    # assumes the next step wanted is the next step in the protocol i.e. doesn't skip one or more steps in the configuration
    # assumes that all artifacts should have the same next step

    def _run(self):

        actions = self.process.step.actions  # obtain the actions of the step # creates a StepActions entity for the current step

        next_actions = actions.next_actions  # obtain the next actions in the step #creates a list of dict for next_actions for the step

        for next_action in next_actions:  # for all artifacts in next_actions update the action to "complete" with the step as the next step in the protocol
            next_action['action'] = 'review'


        actions.put()


def main():
    # Get the default command line options
    p = step_argparser()

    # Parse command line options
    args = p.parse_args()

    # Load the config from the default location
    load_config()

    # Setup the EPP
    action = AssignNextStep(
        args.step_uri, args.username, args.password, args.log_file,
    )

    # Run the EPP
    action.run()


if __name__ == "__main__":
    main()