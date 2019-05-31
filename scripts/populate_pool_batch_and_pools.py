#!/usr/bin/env python
from datetime import date

from EPPs.common import StepEPP


class PopulatePoolBatchPools(StepEPP):
    #populate the pool ids with format YY-MM-DD_PDP_Pool#{1-9}{1,3} where {1-9}{1,3} is the next available number for
    #that date.
    #populate the pool batch ids with format YY-MM-DD_PDP_Batch#{1-9}{1,3} where {1-9}{1,3} is the next available number for
    #that date.
    #populate the output artifact with the prep workflow and adapter type of the input
    _max_nb_output_containers = 1

    def create_pool_batch_id(self):
        today = str(date.today())
        name_template = today + '_PDP_Batch#%d'
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
        self.process.analytes()[0][0].container.put()
        # assumes input artifacts have already been checked to allow only 1 library type at beginning of step
        prep_workflow = self.process.all_inputs()[0].samples[0].udf['Prep Workflow']
        # assumes input artifacts have already been checked to allow only 1 adapter type
        adapter_type = self.lims.get_reagent_types(name=self.process.all_inputs()[0].reagent_labels[0])[0].category

        # Name all pools and assign the prep workflow and adapter type to them then put into LIMS
        for o_art in self.process.analytes()[0]:
            o_art.name = self.create_pool_id()

            o_art.udf['Prep Workflow'] = prep_workflow
            o_art.udf['Adapter Type'] = adapter_type
            o_art.put()


if __name__ == '__main__':
    PopulatePoolBatchPools().run()
