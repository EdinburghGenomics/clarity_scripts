#!/usr/bin/env python
from EPPs.common import StepEPP, step_argparser, get_workflow_stage

class AssignWorkflowSampleReview(StepEPP):
    #Assigns samples to Data Release Trigger if sample measurement UDF SR Useable = Yes

    def _run(self):
        artifact_to_route = set()

        for art in self.output_artifacts:

            if art.udf.get("SR Useable") == "yes":
                artifact_to_route.add(art)
                stage = get_workflow_stage(self.lims, "PostSeqLab EG 1.0 WF",
                                           "Data Release Trigger EG 1.0 ST")
                self.lims.route_artifacts(list(art), stage_uri=stage.uri)
            # assigns the normalised batch plate to the TruSeq PCR-Free workflow




def main():
    p = step_argparser()
    args = p.parse_args()
    action = AssignWorkflowSampleReview(args.step_uri, args.username, args.password, args.log_file)
    action.run()


if __name__ == "__main__":
    main()
