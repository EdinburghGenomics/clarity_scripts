#!/usr/bin/env python
# !/usr/bin/env python
from EPPs.common import step_argparser, StepEPP
from EPPs.config import load_config


class UpdateFreezerLocation(StepEPP):
    def _run(self):
        for artifact in artifacts:
            if re.match('LP[0-9]{7}-DNA', container.name):
                artifact.udf['Freezer'] = self.process.udf.get('New Freezer Location')
                artifact.udf['Shelf'] = self.process.udf.get('New Freezer Location')
                artifact.udf['Box'] = self.process.udf.get('New Freezer Location')
                artifact.put()

            if re.match('\w*P[0-9]{3}', container.name):
                artifact.samples[0].udf['Freezer'] = self.process.udf.get('New Freezer Location')
                artifact.samples[0].udf['Shelf'] = self.process.udf.get('New Freezer Location')
                artifact.samples[0].udf['Box'] = self.process.udf.get('New Freezer Location')
                artifact.samples[0].put()


def main():
    # Get the default command line options
    p = step_argparser()

    # Parse command line options
    args = p.parse_args()

    # Load the config from the default location
    load_config()

    # Setup the EPP
    action = UpdateFreezerLocation(
        args.step_uri, args.username, args.password, args.log_file,
    )

    # Run the EPP
    action.run()


if __name__ == "__main__":
    main()
