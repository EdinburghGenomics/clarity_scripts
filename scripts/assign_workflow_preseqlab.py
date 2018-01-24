#!/usr/bin/env python
from EPPs.common import StepEPP, step_argparser, get_workflow_stage, find_newest_artifact_originating_from


class AssignWorkflowPreSeqLab(StepEPP):

    def _run(self):
        artifacts_to_route = set()
        for art in self.artifacts:
            sample = art.samples[0]
            if sample.udf.get("Proceed To SeqLab") and not sample.udf.get("2D Barcode"):
                # checks to see if sample is in plate or fluidX tube
                artifacts_to_route.add(sample.artifact)

            elif sample.udf.get("Proceed To SeqLab") and sample.udf.get("2D Barcode"):
                artifact = find_newest_artifact_originating_from(
                    self.lims,
                    process_type="FluidX Transfer From Rack Into Plate EG 1.0 ST",
                    sample_name=sample.name
                )
                artifacts_to_route.add(artifact)

        if artifacts_to_route:
            # Only route artifacts if there are any
            stage = get_workflow_stage(self.lims, "PreSeqLab EG 6.0", "Sequencing Plate Preparation EG 2.0")
            self.lims.route_artifacts(list(artifacts_to_route), stage_uri=stage.uri)


def main():
    p = step_argparser()
    args = p.parse_args()
    action = AssignWorkflowPreSeqLab(args.step_uri, args.username, args.password, args.log_file)
    action.run()

if __name__ == "__main__":
    main()
