#!/usr/bin/env python
from datetime import date

from EPPs.common import StepEPP


class PopulateBatchID(StepEPP):
#CST batch ID has the format YY-MM-DD_CST_Batch#{1-9}{1,3} where {1-9}{1,3} represents the next available number for
#that date

    def create_cst_batch_id(self):
        today = str(date.today())
        name_template = today + '_CST_Batch#%d'
        # find next available batch id and use range limit to prevent infinite loop
        for batch_count in range(1, 999):
            new_batch_name = name_template % batch_count
            if not self.lims.get_containers(name=new_batch_name):
                return new_batch_name
        raise ValueError('Cannot allocate more than 999 cst batch IDs with date %s ' % today)

    def _run(self):
        # assign CST Batch ID
        self.process.analytes()[0][0].container.name = self.create_cst_batch_id()
        self.process.analytes()[0][0].container.put()


if __name__ == "__main__":
    PopulateBatchID().run()
