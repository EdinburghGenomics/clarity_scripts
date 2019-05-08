#!/usr/bin/env python
from EPPs.common import StepEPP


class AssignNextStepSampleReceipt(StepEPP):
    """
    This script checks to see if any of the relevant step UDFs are answered indicating that a manager review is required
    """

    def _run(self):

        # obtain the actions of the step then creates a StepActions entity for the current step
        actions = self.process.step.actions

        # obtain the next actions in the step then creates a list of dict for next_actions for the step
        next_actions = actions.next_actions

        # check to see if step UDF has not been completed. If not then set all next actions to "review"
        if self.process.udf['Dry ice remaining in package?'] == 'No' \
                or self.process.udf['Container(s) undamaged and sealed?'] == 'No' \
                or self.process.udf['Samples frozen?'] == 'No' \
                or self.process.udf['Is sample present in wells or tubes?'] == 'No':

            # for all artifacts in next_actions update the action to "review"
            for next_action in next_actions:
                next_action['action'] = 'review'

        else:
            self.next_step_or_complete(next_actions)

        actions.put()


if __name__ == '__main__':
    AssignNextStepSampleReceipt().run()
