#!/usr/bin/env python
from EPPs.common import StepEPP, get_workflow_stage


class AssignWorkflowPostReceiveSample(StepEPP):
    """
    Assigns a dispatched plate to either Sample QC and Plate Prep or User Prepared Library Plate Prep
    """
    def _run(self):
        artifacts_to_route_userprepared = set()
        artifacts_to_route_sampleqc = set()

        for art in self.artifacts:
            sample = art.samples[0]
            if sample.udf.get("User Prepared Library") == "Yes":
                artifacts_to_route_userprepared.add(art)
            else:
                artifacts_to_route_sampleqc.add(art)

        if artifacts_to_route_userprepared:
            # Only route artifacts if there are any artifacts to go to User Prepared Library
            stage = get_workflow_stage(self.lims, "User Prepared Library Receipt and Batch EG 1.0 WF", "User Prepared Library Batch EG 1.0 ST")
            self.lims.route_artifacts(list(artifacts_to_route_userprepared), stage_uri=stage.uri)

        if artifacts_to_route_sampleqc:
            # Only route artifacts if there are any artifacts to go to PreSeqLab
            stage = get_workflow_stage(self.lims, "PreSeqLab EG 6.0", "Spectramax Picogreen EG 6.0")
            self.lims.route_artifacts(list(artifacts_to_route_sampleqc), stage_uri=stage.uri)


if __name__ == "__main__":
    AssignWorkflowPostReceiveSample().run()
