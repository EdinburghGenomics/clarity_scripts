#!/usr/bin/env python
from EPPs.common import StepEPP


class AssignNextStepQuantStudio(StepEPP):
    """
    This script assigns the next step for samples in the QuantStudio Data Import step. It assigns the next step as
    either complete or review depending on whether the number of SNP calls exceeds the minimum number of calls.
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


if __name__ == "__main__":
    AssignNextStepQuantStudio().run()
