#!/usr/bin/env python
from EPPs.common import StepEPP, step_argparser, get_workflow_stage


class AssignWorkflowPreSeqLab(StepEPP):

    def _run(self):
        submitted_arts = []
        for sample in self.samples:
            if sample.udf.get("Proceed To SeqLab") == True:
                submitted_arts.append(sample.artifact)

        stage = get_workflow_stage(self.lims, "PreSeqLab EG 6.0", "Sequencing Plate Preparation EG 2.0")
        self.lims.route_artifacts(submitted_arts, stage_uri=stage.uri)

        # submitted_arts = []
        # for sample in self.samples:
        #     if sample.udf.get("Species") == "Homo sapiens" or sample.udf.get("Species") == "Human":
        #         submitted_arts.append(sample.artifact)
        # stage = get_workflow_stage(self.lims, "QuantStudio EG1.0", "QuantStudio Plate Preparation EG1.0")
        # self.lims.route_artifacts(submitted_arts, stage_uri=stage.uri)


def main():
    p = step_argparser()
    args = p.parse_args()
    action = AssignWorkflowPreSeqLab(args.step_uri, args.username, args.password, args.log_file)
    action.run()

if __name__ == "__main__":
    main()

