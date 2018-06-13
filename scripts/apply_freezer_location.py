#!/usr/bin/env python
import sys
from EPPs.common import StepEPP, step_argparser


class ApplyFreezerLocation(StepEPP):
    """
    Updates submitted sample UDFs for Freezer and Shelf location based on the values provided in step UDFs Freezer and
    Shelf. System exit occurs if step UDF container does not match a sample artifact container name
    """

    def _run(self):
        samples_to_update = set()
        for sample in self.samples:
            if sample.artifact.container.name == self.process.udf['Container Name']:
                sample.udf['Freezer'] = self.process.udf['Freezer']
                sample.udf['Shelf'] = self.process.udf['Shelf']
                samples_to_update.add(sample)
            else:
                print("Container '%s' not present in step" % self.process.udf['Container Name'])
                sys.exit(1)
        self.lims.put_batch(list(samples_to_update))


def main():
    p = step_argparser()
    args = p.parse_args()
    action = ApplyFreezerLocation(args.step_uri, args.username, args.password, args.log_file)
    action.run()


if __name__ == '__main__':
    main()
