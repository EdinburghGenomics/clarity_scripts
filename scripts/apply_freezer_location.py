#!/opt/gls/clarity/users/glsai/Applications/clarity_scripts/UserPreparedLibrary20180523/bin/python3.4
from EPPs.common import StepEPP, step_argparser, get_workflow_stage
import sys


class ApplyFreezerLocation(StepEPP):
    """
    Updates submitted sample UDFs for Freezer and Shelf location based on the values provided in step UDFs Freezer and Shelf
    """

    def _run(self):


        for art in self.artifacts:
            sample = art.samples[0]
            if sample.artifact.container.name == self.process.udf['Container Name']:
                sample.udf['Freezer'] = self.process.udf['Freezer']
                sample.udf['Shelf'] = self.process.udf['Shelf']
                sample.put()

                print(art)
            else:
                print("Container '%s' not present in step" %self.process.udf['Container Name'])
                sys.exit(1)


def main():
    p = step_argparser()
    args = p.parse_args()
    action = ApplyFreezerLocation(args.step_uri, args.username, args.password, args.log_file)
    action.run()


if __name__ == "__main__":
    main()
