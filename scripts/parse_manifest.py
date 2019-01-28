#!/usr/bin/env python
from openpyxl import load_workbook

from EPPs.common import StepEPP


class ParseManifest(StepEPP):
    def _run(self):
        print(self.process.all_outputs(unique=True))
        print(self.process.all_outputs(unique=True)[0].files[0].original_location)

        wb = load_workbook(filename=self.process.all_outputs(unique=True)[0].files[0].original_location)

if __name__ == '__main__':
    ParseManifest().run()