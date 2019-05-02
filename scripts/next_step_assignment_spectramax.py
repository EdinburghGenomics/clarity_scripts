#!/usr/bin/env python
from egcg_core.config import cfg
from pyclarity_lims.entities import Protocol

from EPPs.common import StepEPP


class AssignmentNextStepSpectramax(StepEPP):
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
        steps_dict = {}
        for step in protocol.steps:
            print(step.name)
            steps_dict[step.name] = step

        for next_action in next_actions:

            if self.process.outputs_per_input(next_action['artifact'].id, ResultFile=True)[0].udf.get(
                    'Repeat Picogreen with 1:10 Dilution?'):
                # update the next action to the Picogreen 1-10 Dilution step
                next_action['action'] = 'nextstep'
                next_action['step'] = steps_dict[cfg.query('workflow_stage', 'sample_qc', 'repeat_pico')[1]]

            elif next_action['artifact'].samples[0].udf.get('Prep Workflow') == 'KAPA DNA Sample Prep' \
                    or next_action['artifact'].samples[0].udf.get('PreSeqLab Fragment Analyser Complete'):
                # update the next action to the QC Review step
                next_action['action'] = 'nextstep'
                next_action['step'] = steps_dict[cfg.query('workflow_stage', 'sample_qc', 'qc_review')[1]]

            # all other artifacts should be routed to the fragment analyser step
            else:
                next_action['action'] = 'nextstep'
                next_action['step'] = steps_dict[cfg.query('workflow_stage', 'sample_qc', 'frag_analy')[1]]

        # put the next step actions into LIMS
        actions.put()


if __name__ == '__main__':
    AssignmentNextStepSpectramax().run()
