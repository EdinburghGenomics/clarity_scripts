#!/usr/bin/env python
from EPPs.common import StepEPP


class UpdateFreezerLocation(StepEPP):
    def _run(self):
        for sample in self.samples:
            sample.udf['Freezer'] = self.process.udf.get('New Freezer Location')
            sample.udf['Shelf'] = self.process.udf.get('New Freezer Location')
            sample.udf['Box'] = self.process.udf.get('New Freezer Location')
            sample.put()


if __name__ == '__main__':
    UpdateFreezerLocation().run()