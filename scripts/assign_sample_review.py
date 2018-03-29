#!/usr/bin/env python
from EPPs.common import StepEPP, step_argparser, get_workflow_stage

class AssignWorkflowSampleReview(StepEPP):
    #Assigns samples to Data Release Trigger if sample measurement UDF SR Useable = Yes

    def _run(self):


        for art in self.output_artifacts:

            if art.udf.get("SR Useable") == "Yes":
                stage = get_workflow_stage(self.lims, "Data Release EG 2.0 PR",
                                           "Data Release Trigger")
                self.lims.route_artifacts(list(art), stage_uri=stage.uri)
            # assigns the normalised batch plate to the TruSeq PCR-Free workflow




def main():
    p = step_argparser()
    args = p.parse_args()
    action = AssignWorkflowSampleReview(args.step_uri, args.username, args.password, args.log_file)
    action.run()


if __name__ == "__main__":
    main()
