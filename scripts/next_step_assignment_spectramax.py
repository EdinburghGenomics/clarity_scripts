#!/usr/bin/env python
from EPPs.common import StepEPP
from pyclarity_lims.entities import Protocol


class AssignmentNextStepSpectramax(StepEPP):
    _use_load_config = False  # prevent the loading of the config file
    """
    This script assigns the next step to samples in the Spectramax Picogreen step at initial sample QC. 
    Samples with output udf 'Repeat Picogreen with 1:10 Dilution?' as true will be directed to a dilution step.
    Samples that have the sample udf 'Prep Workflow' as KAPA DNA Sample Prep will skip Fragment Analyser
    and be queued to QC Review. 
    Samples that have gone through the 1:10 Dilution and already completed the Fragment Analyser step will be queued 
    to the QC Review step.
    All other samples with will be queued to Fragment Analyser. 
    """

    def _run(self):
        # obtain the actions of the step then creates a StepActions entity for the current step
        actions = self.process.step.actions

        # obtain the next actions in the step then creates a list of dict for next_actions for the step
        next_actions = actions.next_actions

        # prepare the step_object variable used for inputs that move to the next step
        current_step = self.process.step.configuration  # configuration gives the ProtocolStep entity.
        protocol = Protocol(self.process.lims, uri='/'.join(self.process.step.configuration.uri.split('/')[:-2]))

        steps = protocol.steps  # a list of all the ProtocolSteps in protocol

        for next_action in next_actions:

            if self.process.outputs_per_input(next_action['artifact'].id,ResultFile=True)[0].udf.get('Repeat Picogreen with 1:10 Dilution?'):
                # update the next action to the third step from this step i.e. Picogreen 1-10 Dilution
                next_step_object = steps[steps.index(current_step) + 3]
                next_action['action'] = 'nextstep'
                next_action['step'] = next_step_object

            elif next_action['artifact'].samples[0].udf.get('Prep Workflow') == 'KAPA DNA Sample Prep'\
                    or next_action['artifact'].samples[0].udf.get('PreSeqLab Fragment Analyser Complete'):
                #update the next action to the second step from this step i.e. QC Review
                next_step_object = steps[steps.index(current_step) + 2]
                next_action['action'] = 'nextstep'
                next_action['step'] = next_step_object

            # all other artifacts should be route to remove from workflow as the submitted sample will reassigned elsewhere
            else:


                next_step_object = steps[steps.index(current_step) + 1]
                next_action['action'] = 'nextstep'

                next_action['step'] = next_step_object

        # put the next step actions into LIMS
        actions.put()


if __name__ == '__main__':
    AssignmentNextStepSpectramax().run()
