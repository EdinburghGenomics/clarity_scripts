#!/usr/bin/env python
from EPPs.common import StepEPP
from pyclarity_lims.entities import Protocol
import sys


class AssignNextStepKAPAqPCR(StepEPP):
    """
    This script assigns the next step for samples based on the QC flag of the input artifact and the step UDF
    standard curve result.
    """
    _use_load_config = False  # prevent the loading of the config

    def __init__(self, argv=None):
        super().__init__(argv)


    def _run(self):

        # obtain the actions of the step then creates a StepActions entity for the current step
        actions = self.process.step.actions

        # obtain the next actions in the step then creates a list of dict for next_actions for the step
        next_actions = actions.next_actions

        for next_action in next_actions:
            art = next_action['artifact']
            if art.name.split(' ')[0] == 'QSTD' or art.name.split(' ')[0] == 'No':
                #standards and no template control should never proceed to the next step or repeat
                next_action['action'] = 'remove'

            else:

                if not self.process.udf.get('Standard Curve Result'):
                    print('No value in step UDF "Standard Curve Result". Please complete result parsing and linear regression.')
                    sys.exit(1)

                elif self.process.udf.get('Standard Curve Result') =='Repeat Make and Read qPCR Quant':
                    # check if the Standard Curve passed QC. If not then step should be repeated
                    print(self.process.udf.get('Standard Curve Result'))
                    print(art.name, " assigned as repeat")
                    next_action['action'] = 'repeat'

                else:
                    print(art.qc_flag)
                    if art.qc_flag == 'FAILED':
                        #if an input sample has failed QC then this should go to manager review
                        next_action['action'] = 'review'
                    elif art.qc_flag== 'PASSED':
                        #if an input sample has passed QC then it can be assigned to the next step
                        current_step = self.process.step.configuration  # configuration gives the ProtocolStep entity.
                        protocol = Protocol(self.process.lims,
                                            uri='/'.join(self.process.step.configuration.uri.split('/')[:-2]))
                        steps = protocol.steps  # a list of all the ProtocolSteps in protocol
                        step_object = steps[steps.index(current_step) + 1] #find the next step
                        next_action['action'] ='nextstep'
                        next_action['step']=step_object

        actions.put()


if __name__ == '__main__':
    AssignNextStepKAPAqPCR().run()
