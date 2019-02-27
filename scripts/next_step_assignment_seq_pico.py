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

    def _run(self):
        # Artifacts that are standards next step is "remove".
        # Artifacts where picogreen passed QC next is "complete"
        # Artifacts that are not samples and picogreen did not pass qc then next step is "review"
        for next_action in self.process.step.actions.next_actions:
            art = next_action['artifact']
            if art.name.split(' ')[0] == 'SDNA':
                next_action['action'] = 'remove'
            elif str(art.udf.get("Picogreen Conc Review")).find('FAIL') > -1:
                next_action['action'] = 'review'
            else:
                next_action['action'] = 'complete'

        self.process.step.actions.put()


if __name__ == "__main__":
    AssignNextStepSeqPico().run()
