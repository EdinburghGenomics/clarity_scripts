#!/usr/bin/env python
import platform

import time
from pyclarity_lims.entities import Step
from requests import HTTPError

from EPPs.common import StepEPP, get_workflow_stage, find_newest_artifact_originating_from


class AssignWorkflowPreSeqLab(StepEPP):

    @staticmethod
    def _finish_step(step, try_count=1):
        """
        This function will try to advance a step three time waiting for a ongoing program to finish.
        It waits for 5 seconds in between each try
        """
        try:
            step.get(force=True)
            step.advance()
        except HTTPError as e:
            if try_count < 3 and str(e) == '400: Cannot advance a step that has an external program queued, ' \
                                           'running or pending acknowledgement':
                # wait for whatever needs to happen to happen
                time.sleep(5)
                AssignWorkflowPreSeqLab._finish_step(step, try_count=try_count + 1)
            else:
                raise e

    def _run(self):
        artifacts_to_route_to_seq_lab = set()
        artifacts_to_route_to_remove = set()
        for art in self.artifacts:
            sample = art.samples[0]
            if sample.udf.get("Proceed To SeqLab") and not sample.udf.get("2D Barcode"):
                # checks to see if sample is in plate or fluidX tube
                artifacts_to_route_to_seq_lab.add(sample.artifact)

            elif sample.udf.get("Proceed To SeqLab") and sample.udf.get("2D Barcode"):
                artifact = find_newest_artifact_originating_from(
                    self.lims,
                    process_type="FluidX Transfer From Rack Into Plate EG 1.0 ST",
                    sample_name=sample.name
                )
                artifacts_to_route_to_seq_lab.add(artifact)

            else:
                artifacts_to_route_to_remove.add(sample.artifact)

        if artifacts_to_route_to_seq_lab:
            # Only route artifacts if there are any
            stage = get_workflow_stage(self.lims, "PreSeqLab EG 6.0", "Sequencing Plate Preparation EG 2.0")
            self.lims.route_artifacts(list(artifacts_to_route_to_seq_lab), stage_uri=stage.uri)

        if artifacts_to_route_to_remove:
            stage = get_workflow_stage(self.lims, "Remove From Processing EG 1.0 WF", "Remove From Processing EG 1.0 ST")
            self.lims.route_artifacts(list(artifacts_to_route_to_remove), stage_uri=stage.uri)

            # Create new step with the routed artifacts
            s = Step.create(self.lims, protocol_step=stage.step, inputs=artifacts_to_route_to_remove,
                            container_type_name='Tube')

            url = 'https://%s/clarity/work-complete/%s' % (platform.node(), self.process.id.split('-')[1])
            s.details.udf['Reason for removal from processing:'] = 'Failed QC. See step %s' % url
            s.details.put()

            # Move from "Record detail" window to the "Next Step"
            s.advance()

            for next_action in s.actions.next_actions:
                next_action['action'] = 'complete'
            s.actions.put()

            # Complete the step
            self._finish_step(s)


if __name__ == "__main__":
    AssignWorkflowPreSeqLab().run()
