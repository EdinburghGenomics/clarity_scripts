#!/usr/bin/env python
from EPPs.common import StepEPP, step_argparser, get_workflow_stage


class AssignWorkflowUserPreparedLibrary(StepEPP):
    """
    Assigns a plate created in User Prepared Library to Make and Read qPCR Quant in the Nano workflow. User Prepared
    Libraries are protocol-agnostic so always go to Nano. Submitted sample UDF "SSQC Result" is updated to "Passed" as
    this is required by SeqLab
    """

    def _run(self):
        stage = get_workflow_stage(self.lims, 'TruSeq Nano DNA Sample Prep', 'SEMI-AUTOMATED - Make and Read qPCR Quant')
        self.lims.route_artifacts(self.output_artifacts, stage_uri=stage.uri)
        samples_to_update = set()

        for art in self.output_artifacts:
            sample = art.samples[0]
            sample.udf['SSQC Result'] = 'Passed'
            samples_to_update.add(sample)

        self.lims.put_batch(list(samples_to_update))


def main():
    p = step_argparser()
    args = p.parse_args()
    action = AssignWorkflowUserPreparedLibrary(args.step_uri, args.username, args.password, args.log_file)
    action.run()


if __name__ == '__main__':
    main()
