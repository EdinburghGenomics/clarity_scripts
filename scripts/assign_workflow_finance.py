#!/usr/bin/env python
from EPPs.common import StepEPP, step_argparser, get_workflow_stage, find_newest_artifact_originating_from


class AssignWorkflowFinance(StepEPP):
#All samples for the artifacts in the step will be queued to finance workflow
    def _run(self):
        artifacts_to_route = set()
        for art in self.artifacts:
            sample = art.samples[0]
            artifacts_to_route.add(sample.artifact)

        if artifacts_to_route:
            # Only route artifacts if there are any
            stage = get_workflow_stage(self.lims, "Finance - Invoicing EG 1.0", "Finance - Invoice To Be Sent")
            self.lims.route_artifacts(list(artifacts_to_route), stage_uri=stage.uri)


def main():
    p = step_argparser()
    args = p.parse_args()
    action = AssignWorkflowFinance(args.step_uri, args.username, args.password, args.log_file)
    action.run()

if __name__ == "__main__":
    main()
