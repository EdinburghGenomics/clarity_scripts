#!/usr/bin/env python
# !/usr/bin/env python
from EPPs.common import step_argparser, StepEPP


# the freezer location of the sample entering the step should be updated to match the step UDFs. The script checks
# if the sample is a submitted sample or aderived sample and updates the corresponding UDFs


class UpdateFreezerLocation(StepEPP):
    def _run(self):
        # process each artifact in the step
        for artifact in self.artifacts:
            # if the sample is a submitted sample then the artifact in the step will match the artifact obtained if
            # we obtain the submitted sample and then its equivalent artifact
            if str(artifact) == str(artifact.samples[0].artifact):
                artifact.samples[0].udf['Freezer'] = self.process.udf.get('New Freezer Location')
                artifact.samples[0].udf['Shelf'] = self.process.udf.get('New Freezer Location')
                artifact.samples[0].put()
            # if the sample is a derived sample then the artifact in the step will not match the artifact obtained if
            # we obtain the submitted sample and then its equivalent artifact
            elif str(artifact) != str(artifact.samples[0].artifact):
                artifact.udf['Freezer'] = self.process.udf.get('New Freezer Location')
                artifact.udf['Shelf'] = self.process.udf.get('New Freezer Location')
                artifact.put()


def main():
    # Get the default command line options
    p = step_argparser()

    # Parse command line options
    args = p.parse_args()

    # Setup the EPP
    action = UpdateFreezerLocation(
        args.step_uri, args.username, args.password, args.log_file,
    )

    # Run the EPP
    action.run()


if __name__ == "__main__":
    main()
