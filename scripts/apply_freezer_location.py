#!/usr/bin/env python
from EPPs.common import StepEPP, step_argparser, get_workflow_stage


class ApplyFreezerLocation(StepEPP):
    """
    Updates submitted sample UDFs for Freezer and Shelf location based on the values provided in step UDFs Freezer and Shelf
    """

    def _run(self):


        for art in self.output_artifacts:
            sample = art.samples[0]
            if  sample_container_name== self.process.udf['Container Name']:
                sample.udf['Freezer'] = self.process.udf['Freezer']
                sample.udf['Shelf'] = self.process.udf['Shelf']
                sample.put()
            else:
                raise ValueError('Container scanned does not match container in step')



def main():
    p = step_argparser()
    args = p.parse_args()
    action = ApplyFreezerLocation(args.step_uri, args.username, args.password, args.log_file)
    action.run()


if __name__ == "__main__":
    main()
