#!/usr/bin/env python
from EPPs.common import StepEPP, step_argparser, get_workflow_stage

class AssignWorkflowSampleReview(StepEPP):
    #Checks if output artifact is "SR Useable = yes" then finds the submitted sample for that artifact
    #  and assigns the submitted sample to Data Release Trigger

    def _run(self):
        artifact_to_route = set()

        for art in self.output_artifacts:

            if art.udf.get("SR Useable") == "yes":
                sample=art.samples[0]
                artifact_to_route.add(sample.artifact)
                stage = get_workflow_stage(self.lims, "PostSeqLab EG 1.0 WF",
                                           "Data Release Trigger EG 1.0 ST")
                self.lims.route_artifacts(list(artifact_to_route
                                               ), stage_uri=stage.uri)

def main():
    p = step_argparser()
    args = p.parse_args()
    action = AssignWorkflowSampleReview(args.step_uri, args.username, args.password, args.log_file)
    action.run()


if __name__ == "__main__":
    main()
