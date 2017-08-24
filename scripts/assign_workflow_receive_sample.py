#!/usr/bin/env python
from EPPs.common import StepEPP, step_argparser, get_workflow_stage

class AssignWorkflowReceiveSample(StepEPP):
    #Assign received plate to either User Prepared Library Batch or Spectramax Picogreen

    def _run(self):
        artifact_to_route_userprepared = set()
        artifact_to_route_preseqlab = set()


        for art in self.artifacts:
            sample = art.samples[0]
            if sample.udf.get("User Prepared Library") == "Yes":
                artifact_to_route_userprepared.add(art)
            # assigns the received sample to User Prepared Library Batch if is a user prepared library


            elif not sample.udf.get("User Prepared Library"):
                artifact_to_route_preseqlab.add(art)
                # assigns the received sample to PreSeqLab if NOT an user prepared library

        if artifact_to_route_userprepared:
            # Only route artifacts if there are any artifacts to go to PCR-Free
            stage = get_workflow_stage(self.lims, "User Prepared Library Batch EG1.0 WF", "User Prepared Library Batch EG 1.0 ST")
            self.lims.route_artifacts(list(artifact_to_route_userprepared), stage_uri=stage.uri)

        if artifact_to_route_preseqlab:
            # Only route artifacts if there are any artifacts to go to Nano
            stage = get_workflow_stage(self.lims, "PreSeqLab EG 6.0", "Spectramax Picogreen EG 6.0")
            self.lims.route_artifacts(list(artifact_to_route_preseqlab), stage_uri=stage.uri)



def main():
    p = step_argparser()
    args = p.parse_args()
    action = AssignWorkflowReceiveSample(args.step_uri, args.username, args.password, args.log_file)
    action.run()


if __name__ == "__main__":
    main()