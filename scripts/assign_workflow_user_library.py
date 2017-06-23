#!/usr/bin/env python
from EPPs.common import StepEPP, step_argparser, get_workflow_stage,

class AssignWorkflowUserPreparedLibrary(StepEPP):
    #Assign plate created in User Prepared Library to either Nano or PCR Free workflow

    def _run(self):
        artifact_to_route_pcr_free = set()
        artifact_to_route_nano = set()

        for art in self.output_artifacts:
            sample = art.samples[0]
            if sample.udf.get("Prep Workflow") == "TruSeq PCR-Free DNA Sample Prep":
                artifact_to_route_pcr_free.add(art)
            # assigns the normalised batch plate to the TruSeq PCR-Free workflow


            elif sample.udf.get("Prep Workflow") == "TruSeq Nano DNA Sample Prep":
                artifact_to_route_nano.add(art)
                # assigns the normalised batch plate to the TruSeq Nano workflow

        if artifact_to_route_pcr_free:
            # Only route artifacts if there are any artifacts to go to PCR-Free
            stage = get_workflow_stage(self.lims, "TruSeq PCR-Free DNA Sample Prep", "SEMI-AUTOMATED - Make and Read qPCR Quant")
            self.lims.route_artifacts(list(artifact_to_route_pcr_free), stage_uri=stage.uri)

        if artifact_to_route_nano:
            # Only route artifacts if there are any artifacts to go to Nano
            stage = get_workflow_stage(self.lims, "TruSeq Nano DNA Sample Prep", "SEMI-AUTOMATED - Make LQC & Caliper GX QC")
            self.lims.route_artifacts(list(artifact_to_route_nano), stage_uri=stage.uri)



def main():
    p = step_argparser()
    args = p.parse_args()
    action = AssignWorkflowUserPreparedLibrary(args.step_uri, args.username, args.password, args.log_file)
    action.run()


if __name__ == "__main__":
    main()
