#!/usr/bin/env python
from EPPs.common import step_argparser, StepEPP
from EPPs.config import load_config
# from pyclarity_lims.entities import ProtocolStep
from pyclarity_lims.entities import Protocol


class AssignNextStep(
    StepEPP):  # finds the next step in the protocol and assigns it to the artifacts appearing in the Next Steps of the script -
    # assumes the next step wanted is the next step in the protocol i.e. doesn't skip one or more steps in the configuration
    # assumes current step is not the last step in the protocol

    def _run(self):
        current_step_name = self.process.step.configuration.name  # configuration gives the ProtocolStep entity. Will use ProtocolStep name as the ProtoclStep obtained
        # this way is missing the url so doesn't match the ProtocolStep created from the Protocol entity

        protocol = Protocol(self.process.lims, uri='/'.join(self.process.step.configuration.uri.split('/')[:-2]))

        actions = self.process.step.actions  #  creates a StepActions entity for the current step

        next_actions = actions.next_actions  # creates a list of dict containing details of the next_actions for the step

        steps = protocol.steps  # a list of all the ProtocolSteps in protocol

        for step in steps:  # find the index of the current step in the list of all ProtocolSteps then assign the step_object as the next step in the list
            if step.name == current_step_name:
                step_object = steps[steps.index(step) + 1]

        for next_action in next_actions:  # for all artifacts in next_actions update the action to "next step" with the step as the next step in the protocol
            next_action['action'] = 'nextstep'
            next_action['step'] = step_object

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