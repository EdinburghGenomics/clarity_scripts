#!/usr/bin/env python
from datetime import date

from EPPs.common import StepEPP


class PopulatePoolBatchPools(StepEPP):
    _max_nb_output_containers = 1

    def create_pool_batch_id(self):
        today = str(date.today())
        name_template = 'PDP_Batch_ID:_' + today + '_PDP_Batch#%d'
        # find next available batch id and use range limit to prevent infinite loop
        for batch_count in range(1, 999):
            new_batch_name = name_template % batch_count
            if not self.lims.get_containers(name=new_batch_name):
                return new_batch_name
        raise ValueError('Cannot allocate more than 999 pool batch IDs with date %s ' % today)

    def create_pool_id(self):
        today = str(date.today())
        name_template = today + '_PDP_Pool#%d'

        # find next available batch id and use range limit to prevent infinite loop
        for pool_count in range(1, 999):
            new_pool_name = name_template % pool_count

            if not self.lims.get_artifacts(name=new_pool_name):
                return new_pool_name
        raise ValueError('Cannot allocate more than 999 pool IDs with date %s ' % today)

    def _run(self):
        # output analytes obtained by self.process.analytes
        self.process.analytes()[0][0].container.name = self.create_pool_batch_id()
        # assumes input artifacts have already been checked to allow only 1 library type at beginning of step

        prep_workflow = self.process.all_inputs()[0].samples[0].udf['Prep Workflow']
        # assumes input artifacts have already been checked to allow only 1 adapter type
        adapter_type = self.lims.get_reagent_types(name=self.process.all_inputs()[0].reagent_labels[0])[0].category

        # Name all pools and assign the prep workflow and adapter type to them
        for o_art in self.process.analytes()[0]:
            o_art.name = self.create_pool_id()

            o_art.udf['Prep Workflow'] = prep_workflow
            o_art.udf['Adapter Type'] = adapter_type

        # put the updated pools into the lims
        self.lims.put_batch(self.process.analytes()[0])

if __name__ == '__main__':
    PopulatePoolBatchPools().run()