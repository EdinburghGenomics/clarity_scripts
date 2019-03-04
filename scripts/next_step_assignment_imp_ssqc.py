#!/usr/bin/env python
from EPPs.common import StepEPP
from pyclarity_lims.entities import Protocol


class AssignNextStep(StepEPP):
    _use_load_config = False  # prevent the loading of the config file
    """
    This script assigns all output artifacts in a container that has a name with suffix "-IMP" into a step in the same protocol defined by the '-m'
    argument and all the output artifacts that has a name with suffix "-SSQC" into a step in the same protocol defined by the '-q' argument
    """
    def __init__(self, argv=None):
        super().__init__(argv)
        self.imp = self.cmd_args.imp
        self.ssqc = self.cmd_args.ssqc

    @staticmethod
    def add_args(argparser):
        argparser.add_argument('-m', '--imp',  type=str, required=True, help='Set the next step in protocol for -IMP')
        argparser.add_argument('-q', '--ssqc',  type=str, required=True, help='Set the next step in protocol for -SSQC')


    def _run(self):

        # obtain the actions of the step then creates a StepActions entity for the current step
        actions = self.process.step.actions

        # obtain the next actions in the step then creates a list of dict for next_actions for the step
        next_actions = actions.next_actions

        #obtain the list of steps in the protocol
        protocol = Protocol(self.process.lims, uri='/'.join(self.process.step.configuration.uri.split('/')[:-2]))
        steps = protocol.steps  # a list of all the ProtocolSteps in protocol

        #obtain the step object for the steps with names matching the arguments
        for step in steps:
            if step.name==self.imp:
                imp_next_step_object=step
            elif step.name==self.ssqc:
                ssqc_next_step_object=step

        #go through all of the "next actions" and the corresponding artifact and assign to the correct next step based on the suffix
        #of the container name.
        for next_action in next_actions:

            if next_action['artifact'].location[0].name.split('-')[1]=='IMP':
                next_action['action'] = 'nextstep'
                next_action['step'] = imp_next_step_object

            if next_action['artifact'].location[0].name.split('-')[1]=='SSQC':
                next_action['action'] = 'nextstep'
                next_action['step'] = ssqc_next_step_object


        actions.put()


if __name__ == '__main__':
    AssignNextStep().run()
