#!/usr/bin/env python
from egcg_core.config import cfg

from EPPs.common import StepEPP, get_workflow_stage, find_newest_artifact_originating_from


class AssignWorkflowSeqLabQuantStudio(StepEPP):
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
                        process_type=cfg.query('process_type', 'fluidx_transfer'),
                        sample_name=sample.name
                    )
                    artifacts_to_route_quant.add(artifact)

        if artifacts_to_route_pcr_free:
            stage_wf_st = cfg.query('workflow_stage', 'pcr-free','start')
            stage = get_workflow_stage(self.lims, stage_wf_st[0], stage_wf_st[1])
            self.lims.route_artifacts(list(artifacts_to_route_pcr_free), stage_uri=stage.uri)

        if artifacts_to_route_nano:
            stage_wf_st = cfg.query('workflow_stage', 'nano','start')
            stage = get_workflow_stage(self.lims, stage_wf_st[0], stage_wf_st[1])
            self.lims.route_artifacts(list(artifacts_to_route_nano), stage_uri=stage.uri)

        if artifacts_to_route_kapa:
            stage_wf_st = cfg.query('workflow_stage', 'kapa','start')
            stage = get_workflow_stage(self.lims, stage_wf_st[0], stage_wf_st[1])
            self.lims.route_artifacts(list(artifacts_to_route_kapa), stage_uri=stage.uri)

        if artifacts_to_route_quant:
            stage_wf_st = cfg.query('workflow_stage', 'quantstudio','start')
            stage = get_workflow_stage(self.lims, stage_wf_st[0], stage_wf_st[1])
            self.lims.route_artifacts(list(artifacts_to_route_quant), stage_uri=stage.uri)


if __name__ == "__main__":
    AssignWorkflowSeqLabQuantStudio().run()
