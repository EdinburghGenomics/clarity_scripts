#!/usr/bin/env python
from EPPs.common import StepEPP, get_workflow_stage, find_newest_artifact_originating_from


class AssignWorkflowSeqLabQuantStudio(StepEPP):
    _use_load_config = False  # prevent the loading of the config file
    """
    Assigns plates of submitted samples or FluidX derived artifacts to the correct library prep workflow and assigns to the
    QuantStudio workflow if required based on UDFs "Prep Workflow", "Species" and "Skip genotyping for (human) sample?"
    """

    def _run(self):
        artifacts_to_route_pcr_free = set()
        artifacts_to_route_nano = set()
        artifacts_to_route_quant = set()
        artifacts_to_route_kapa = set()

        for art in self.output_artifacts:
            sample = art.samples[0]
            if sample.udf.get("Prep Workflow") == "TruSeq PCR-Free DNA Sample Prep":
                artifacts_to_route_pcr_free.add(art)

            elif sample.udf.get("Prep Workflow") == "TruSeq Nano DNA Sample Prep":
                artifacts_to_route_nano.add(art)

            elif sample.udf.get("Prep Workflow") == "KAPA DNA Sample Prep":
                artifacts_to_route_kapa.add(art)

            if sample.udf.get("Species") in ("Homo sapiens", "Human") and not sample.udf.get(
                    "Skip genotyping for (human) sample?"):
                # assign either the submitted sample plate or the FluidX derived plate to the QuantStudio
                # workflow if human samples and the lab manager has not selected "Skip genotyping for (human) sample?"

                if not sample.udf.get("2D Barcode"):
                    # check to see if sample is in plate or fluidX tube
                    artifacts_to_route_quant.add(sample.artifact)

                else:
                    artifact = find_newest_artifact_originating_from(
                        self.lims,
                        process_type="FluidX Transfer From Rack Into Plate EG 1.0 ST",
                        sample_name=sample.name
                    )
                    artifacts_to_route_quant.add(artifact)

        if artifacts_to_route_pcr_free:
            stage = get_workflow_stage(self.lims, "TruSeq PCR-Free DNA Sample Prep", "Visual QC")
            self.lims.route_artifacts(list(artifacts_to_route_pcr_free), stage_uri=stage.uri)

        if artifacts_to_route_nano:
            stage = get_workflow_stage(self.lims, "TruSeq Nano DNA Sample Prep", "Visual QC")
            self.lims.route_artifacts(list(artifacts_to_route_nano), stage_uri=stage.uri)

        if artifacts_to_route_kapa:
            stage = get_workflow_stage(self.lims, "KAPA Non-Pooling Sample Prep EG 1.0 WFDEV2",
                                       "Sequencing Plate Picogreen EG 1.0 ST")

            self.lims.route_artifacts(list(artifacts_to_route_kapa), stage_uri=stage.uri)

        if artifacts_to_route_quant:
            stage = get_workflow_stage(self.lims, "QuantStudio EG1.0", "QuantStudio Plate Preparation EG1.0")
            self.lims.route_artifacts(list(artifacts_to_route_quant), stage_uri=stage.uri)


if __name__ == "__main__":
    AssignWorkflowSeqLabQuantStudio().run()
