#!/usr/bin/env python
from EPPs.common import StepEPP
from pyclarity_lims.entities import Protocol


class AssignNextStepSampleReceipt(StepEPP):
    """
    This script checks to see if any of the relevant step UDFs are answered indicating that a manager review is required
    """

    def _run(self):

        # obtain the actions of the step then creates a StepActions entity for the current step
        actions = self.process.step.actions

        # obtain the next actions in the step then creates a list of dict for next_actions for the step
        next_actions = actions.next_actions

        # check to see if review argument flag is present, if 'true' then set all next actions to "review"
        if self.process.udf['Dry ice remaining in package?'] =='No' or self.process.udf['Container(s) undamaged and sealed?'] == 'No'\
            or self.process.udf['Samples frozen?'] == 'No' or self.process.udf['>= 50ul sample present in wells or tubes?']=='No':
            # for all artifacts in next_actions update the action to "review"
            for next_action in next_actions:
                next_action['action'] = 'review'

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
    AssignNextStepSampleReceipt().run()
