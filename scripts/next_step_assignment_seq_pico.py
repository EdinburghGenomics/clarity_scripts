#!/usr/bin/env python
from EPPs.common import StepEPP
from pyclarity_lims.entities import Protocol


class AssignNextStepSeqPico(StepEPP):
    _use_load_config = False  # prevent the loading of the config

    """
    This script assigns the next step for samples in the Sequencing Plate Picgreen step to either "review" if they
    have failed or complete (as last step in the protocol).
    """

    def __init__(self, argv=None):
        super().__init__(argv)

    def _run(self):

        # obtain the actions of the step then creates a StepActions entity for the current step
        actions = self.process.step.actions
        current_step = self.process.step.configuration  # configuration gives the ProtocolStep entity.
        protocol = Protocol(self.process.lims, uri='/'.join(self.process.step.configuration.uri.split('/')[:-2]))
        steps = protocol.steps  # a list of all the ProtocolSteps in protocol
        # obtain the next actions in the step then creates a list of dict for next_actions for the step for all artifacts
        next_actions = actions.next_actions

        # #Artifacts that are standards next step is "remove". Artifacts where picogreen passed QC next is "complete"
        # Artifacts that are not samples and picogreen did not pass qc then next step is "review"
        for next_action in next_actions:
            art = next_action['artifact']
            if art.name.split(' ')[0] == 'SDNA':
                next_action['action'] = 'remove'
            elif str(art.udf.get("Picogreen Conc Review")).find('FAIL'):
                next_action['action'] = 'review'
            else:
                next_action['action'] = 'complete'

        actions.put()


if __name__ == "__main__":
    AssignNextStepSeqPico().run()
