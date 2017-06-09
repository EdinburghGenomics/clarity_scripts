#!/usr/bin/env python
from EPPs.common import StepEPP, step_argparser, get_workflow_stage

def get_parent_process_id(art):
    return art.parent_process.id

class AssignWorkflowSeqLabQuantStudio(StepEPP):
#Assigns plate submitted samples or FluidX derived artifacts to the correct SeqLab Workflow and
#assigns to QuantStudio workflow if required based on the contents of submitted sample UDFs.
#"Prep Workflow", "Species", "Skip genotyping for (human) sample?"

    def _run(self):
        artifact_to_route_pcr_free = set()
        artifact_to_route_nano = set()
        artifact_to_route_quant = set()

        for art in artifacts:
            sample = art.samples[0]
            if art.samples[0].udf.get("Prep Workflow") == "TruSeq PCR-Free DNA Sample Prep":
                artifact_to_route_pcr_free.add(art)
            #assigns the normalised batch plate to the TruSeq PCR-Free workflow


            if art.samples[0].udf.get("Prep Workflow") == "TruSeq Nano DNA Sample Prep":
                artifact_to_route_nano.add(art)
             #assigns the normalised batch plate to the TruSeq Nano workflow

            if sample.udf.get("Species") == "Homo sapiens" and not sample.udf.get("Skip genotyping for (human) sample?")
                or sample.udf.get("Species") == "Human" and not sample.udf.get("Skip genotyping for (human) sample?"):

            #assigns either the submitted sample plate or the FluidX derived plate to the QuantStudio
            #workflow if a human samples and the lab manager has not selected "Skip genotyping for (human)
            #sample?"

                    if not sample.udf.get("2D Barcode"):
                        # checks to see if sample is in plate or fluidX tube
                        artifact_to_route_quant.add(sample.artifact)

                    elif sample.udf.get("2D Barcode"):
                        # if is a fluidX tube will need to find the derived artifact created by the FluidX Transfer step
                        fluidX_artifacts = self.lims.get_artifacts(
                            process_type="FluidX Transfer From Rack Into Plate EG 1.0 ST",
                            sample_name=sample.name,
                            type='Analyte'
                        )

                        if len(fluidX_artifacts) > 1:
                            # its possible that the FluidX Transfer has occurred more than once
                            # so must find the most recent occurrence of that step
                            fluidX_artifacts.sort(key=get_parent_process_id, reverse=True)
                            # sorts the artifacts returned to place the most recent artifact at position 0 in list

                        artifact_to_route_quant.add(fluidX_artifacts[0])

        if artifact_to_route_pcr_free:
            # Only route artifacts if there are any artifacts to go to PCR-Free
            stage = get_workflow_stage(self.lims, "TruSeq PCR-Free DNA Sample Prep", "Visual QC")
            self.lims.route_artifacts(list(artifact_to_route_pcr_free), stage_uri=stage.uri)

        if artifact_to_route_nano:
            # Only route artifacts if there are any artifacts to go to Nano
            stage = get_workflow_stage(self.lims, "TruSeq Nano DNA Sample Prep", "Visual QC")
            self.lims.route_artifacts(list(artifact_to_route_nano), stage_uri=stage.uri

        if artifact_to_route_quant:
            # Only route artifacts if there are any artifacts to go to Nano
            stage = get_workflow_stage(self.lims, "QuantStudio EG1.0", "QuantStudio Plate Preparation EG1.0")
            self.lims.route_artifacts(list(artifact_to_route_quant), stage_uri=stage.uri)

def main():
    p = step_argparser()
    args = p.parse_args()
    action = AssignWorkflowSeqLabQuantStudio(args.step_uri, args.username, args.password, args.log_file)
    action.run()

if __name__ == "__main__":
    main()
