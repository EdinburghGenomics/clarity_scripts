#!/usr/bin/env python
from EPPs.common import StepEPP, step_argparser, get_workflow_stage


class AssignWorkflowUserPreparedLibrary(StepEPP):
    """
    Assigns a plate created in User Prepared Library to the Make and read qPCR Quant in the Nano workflow
    - User Prepared Libraries are protocol "agnostic" so always go to Nano.
    Submitted sample UDF "SSQC Result" is updated to "Passed" as this is required by SeqLab
    """

    def _run(self):
        stage = get_workflow_stage(self.lims, "TruSeq Nano DNA Sample Prep",
                                   "SEMI-AUTOMATED - Make and Read qPCR Quant")
        for art in self.output_artifacts:
            sample = art.samples[0]
            sample.udf['SSQC Result'] = 'Passed'
            sample.put()
        self.lims.route_artifacts(self.output_artifacts, stage_uri=stage.uri)


def main():
    p = step_argparser()
    args = p.parse_args()
    action = AssignWorkflowUserPreparedLibrary(args.step_uri, args.username, args.password, args.log_file)
    action.run()


if __name__ == "__main__":
    main()
