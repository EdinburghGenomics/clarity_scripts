#!/usr/bin/env python
from EPPs.common import step_argparser, StepEPP
from EPPs.config import load_config


class UpdateFreezerLocation(StepEPP):
    def _run(self):
        artifacts = self.process.all_inputs()
        samples = self.samples

        for sample in samples:
            sample.udf['Freezer'] = self.process.udf.get('New Freezer Location')
            sample.udf['Shelf'] = self.process.udf.get('New Freezer Location')
            sample.udf['Box'] = self.process.udf.get('New Freezer Location')
            sample.put()


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