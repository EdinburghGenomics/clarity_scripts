#!/usr/bin/env python
from EPPs.common import step_argparser, StepEPP


class AssignNextStepQuantStudio(StepEPP):
    """
    This script assigns the next step for all samples in the step as either "review","complete" or "nextstep"
    for next step it assumes the next step wanted is the next step in the protocol i.e. doesn't skip one or more steps
    in the configuration assumes that all artifacts should have the same next step
    """

    def _run(self):

        # obtain the actions of the step then creates a StepActions entity for the current step
        actions = self.process.step.actions

        # obtain the next actions in the step then creates a list of dict for next_actions for the step for all artifacts
        next_actions = actions.next_actions

        # check to see if the number of SNP calls in the  parsed data is above or below the threshold and assign next
        # step to either manager review or complete and assign QuantStudio QC flag for submitted sample
        for next_action in next_actions:
            art = next_action['artifact']
            sample = art.samples[0]
            if sample.udf.get("Number of Calls (Best Run)") < self.process.udf.get("Minimum Number of Calls"):
                sample.udf["QuantStudio QC"] = "FAIL"
                sample.put()
                next_action['action'] = 'review'
            elif sample.udf.get("Number of Calls (Best Run)") >= self.process.udf.get("Minimum Number of Calls"):
                sample.udf["QuantStudio QC"] = "PASS"
                sample.put()
                next_action['action'] = 'complete'

        actions.put()


def main():
    # Get the default command line options
    p = step_argparser()

    # Parse command line options
    args = p.parse_args()

    # Setup the EPP
    action = AssignNextStepQuantStudio(
        args.step_uri, args.username, args.password, args.log_file
    )

    # Run the EPP
    action.run()


if __name__ == "__main__":
    main()
