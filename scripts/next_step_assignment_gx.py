#!/usr/bin/env python
from EPPs.common import StepEPP
from pyclarity_lims.entities import Protocol


class AssignNextStep(StepEPP):
    _use_load_config = False  # prevent the loading of the config file
    """
    This script assigns Next Step as either "remove from protocol" if SSQC Results = "PASSED" or "request manager 
    review" if SSQC Reults contains "FAILED"
    """

    def _run(self):

        # obtain the actions of the step then creates a StepActions entity for the current step
        actions = self.process.step.actions

        # obtain the next actions in the step then creates a list of dict for next_actions for the step
        next_actions = actions.next_actions

        #go through all of the "next actions" and the corresponding artifact and assign to the correct next step based
        #on the SSQC Result
        for next_action in next_actions:

            if next_action['artifact'].udf['SSQC Result']=='PASSED':
                next_action['action'] = 'remove'


            else:
                next_action['action'] = 'review'



        actions.put()


if __name__ == '__main__':
    AssignNextStep().run()
