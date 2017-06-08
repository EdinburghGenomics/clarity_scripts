#!/usr/bin/env python
from EPPs.common import StepEPP, step_argparser, get_workflow_stage


def get_parent_process_id(art):
    return art.parent_process.id


class AssignWorkflowPreSeqLab(StepEPP):

    def _run(self):
        artifact_to_route = set()
        for art in self.artifacts:
            sample = art.samples[0]
            if sample.udf.get("Proceed To SeqLab") and not sample.udf.get("2D Barcode"):
                # checks to see if sample is in plate or fluidX tube
                artifact_to_route.add(sample.artifact)

            elif sample.udf.get("Proceed To SeqLab") and sample.udf.get("2D Barcode"):
                print(2D Barcode)
                # if is a fluidX tube will need to find the derived artifact created by the FluidX Transfer step
                fluidX_artifacts = self.lims.get_artifacts(
                    process_type="FluidX Transfer From Rack Into Plate EG 1.0 ST",
                    sample_name=sample.name,
                    type='Analyte'
                )

                if len(fluidX_artifacts) >1:
                    # its possible that the FluidX Transfer has occurred more than once
                    # so must find the most recent occurrence of that step
                    fluidX_artifacts.sort(key=get_parent_process_id, reverse=True)
                    # sorts the artifacts returned to place the most recent artifact at position 0 in list

                artifact_to_route.add(fluidX_artifacts[0])

        if artifact_to_route:
            # Only route artifacts if there are any
            stage = get_workflow_stage(self.lims, "PreSeqLab EG 6.0", "Sequencing Plate Preparation EG 2.0")
            print(artifact_to_route)
            self.lims.route_artifacts(list(artifact_to_route), stage_uri=stage.uri)


def main():
    p = step_argparser()
    args = p.parse_args()
    action = AssignWorkflowPreSeqLab(args.step_uri, args.username, args.password, args.log_file)
    action.run()

if __name__ == "__main__":
    main()

