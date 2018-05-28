#!/usr/bin/env python
from EPPs.common import step_argparser, StepEPP
from pyclarity_lims.entities import Protocol

class AssignNextStepUPL(StepEPP):
    """
    This script assigns the next step for samples in the User Prepared Library Plate Receipt step. It assigns the next step as
    either the next step or review depending on whether the plate condition step UDFs are answered as Yes or No by
    the lab team.
    """

    def _run(self):

        # obtain the actions of the step then creates a StepActions entity for the current step
        actions = self.process.step.actions

        # obtain the next actions in the step then creates a list of dict for next_actions for the step for all artifacts
        next_actions = actions.next_actions

        # check step UDFs answered by lab team to confirm that sample is in good condition. If UDFs both answered "Yes" then
        # set next action as the next step, if one or more UDF is set to "No" then set as "review". The next step in the protocol
        # is found rather than hard coded.

        for next_action in next_actions:

            if self.process.udf.get("Plate(s) Undamaged and Sealed?") == 'No':
                next_action['action'] = 'review'
            elif self.process.udf.get("Samples Present and Frozen in Wells?") == 'No':
                next_action['action'] = 'review'

            else:
                current_step = self.process.step.configuration  # configuration gives the ProtocolStep entity.
                protocol = Protocol(self.process.lims,
                                    uri='/'.join(self.process.step.configuration.uri.split('/')[:-2]))
                steps = protocol.steps  # a list of all the ProtocolSteps in protocol
                step_object = steps[steps.index(current_step) + 1]
                next_action['action'] = 'nextstep'
                next_action['step'] = step_object

        actions.put()


def main():
    # Get the default command line options
    p = step_argparser()

    # Parse command line options
    args = p.parse_args()

    # Setup the EPP
    action = AssignNextStepUPL(
        args.step_uri, args.username, args.password, args.log_file
    )

    # Run the EPP
    action.run()


if __name__ == "__main__":
    main()
