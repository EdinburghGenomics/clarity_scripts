#!/usr/bin/env python
from EPPs.common import StepEPP
from pyclarity_lims.entities import Protocol


class AssignNextStep(StepEPP):
    _use_load_config = False  # prevent the loading of the config file
    """
    This script checks the KAPA Next Step udf and assigns the input sample to the next step in the protocol or to remove from workflow 
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
        step_object = steps[steps.index(current_step) + 1]

        for next_action in next_actions:
            # if KAPA Next Step is KAPA Make Normalised Libraries then assign to next step in the protocol (assumes next step is KAPA Make Normalised Libraries)

            if next_action['artifact'].udf.get('KAPA Next Step') == 'KAPA Make Normalised Libraries':
                # update the next action to "next step" with the step
                next_action['action'] = 'nextstep'
                next_action['step'] = step_object

            # all other artifacts should be route to remove from workflow as the submitted sample will reassigned elsewhere
            else:
                next_action['action'] = 'remove'

        # put the next step actions into LIMS
        actions.put()


if __name__ == '__main__':
    AssignNextStep().run()
