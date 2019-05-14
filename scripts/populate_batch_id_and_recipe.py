#!/usr/bin/env python
from datetime import date

from EPPs.common import StepEPP


class PopulateBatchIDRecipe(StepEPP):

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
        #assign CST Batch ID
        self.process.analytes()[0][0].container.name = self.create_cst_batch_id()
        self.process.analytes()[0][0].container.put()

        #change the recipe to pooling if any input artifacts are pools
        recipe='HiSeqXRecipe.xml'
        for art in self.artifacts:
            if art.container.name[-3:] == 'PDP':
                recipe='HiSeqXRecipe-Pooled.xml'

        #set the recipe in the relevant step UDF

        self.process.udf['Sequencing Run Configuration'] = recipe
        self.process.put()

if __name__ == "__main__":
    PopulateBatchIDRecipe().run()