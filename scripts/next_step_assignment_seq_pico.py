#!/usr/bin/env python
from EPPs.common import step_argparser, StepEPP
from pyclarity_lims.entities import Protocol


class AssignNextStepSeqPico(StepEPP):
    """
    This script assigns the next step for samples in the Sequencing Plate Picgreen step to either "review" if they
    have failed or complete (as last step in the protocol).
    """

    def _run(self):

        # obtain the actions of the step then creates a StepActions entity for the current step
        actions = self.process.step.actions
        current_step = self.process.step.configuration  # configuration gives the ProtocolStep entity.
        protocol = Protocol(self.process.lims, uri='/'.join(self.process.step.configuration.uri.split('/')[:-2]))
        steps = protocol.steps  # a list of all the ProtocolSteps in protocol
        # obtain the next actions in the step then creates a list of dict for next_actions for the step for all artifacts
        next_actions = actions.next_actions

        # check to see if the number of SNP calls in the  parsed data is above or below the threshold and assign next
        # step to either manager review or complete and assign QuantStudio QC flag for submitted sample
        for next_action in next_actions:
            art = next_action['artifact']
            if 'FAIL' in art.udf.get("Picogreen Conc Review"):
                next_action['action'] = 'review'
            else:
                next_action['action'] = 'complete'

        actions.put()


def main():
    # Get the default command line options
    p = step_argparser()

    # Parse command line options
    args = p.parse_args()

    # Setup the EPP
    action = AssignNextStepSeqPico(
        args.step_uri, args.username, args.password, args.log_file
    )

    # Run the EPP
    action.run()


if __name__ == "__main__":
    main()
