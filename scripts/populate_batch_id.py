#!/usr/bin/env python
from datetime import date

from EPPs.common import StepEPP


class PopulateBatchID(StepEPP):
#CST batch ID has the format YY-MM-DD_CST_Batch#{1-9}{1,3} where {1-9}{1,3} represents the next available number for
#that date. Assigns the Adapter Type and Prep Workflow udfs for all output analytes

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
        #assing Adapter Type and Prep Workflow UDFs for all output analytes
        # assumes input artifacts have already been checked to allow only 1 adapter type
        adapter_type = self.lims.get_reagent_types(name=self.process.all_inputs()[0].reagent_labels[0])[0].category
        # assumes input artifacts have already been checked to allow only 1 library type at beginning of step
        prep_workflow = self.process.all_inputs()[0].samples[0].udf['Prep Workflow']
        # Name all pools and assign the prep workflow and adapter type to them then put into LIMS
        for i_art in self.artifacts:
            for o_art in self.process.outputs_per_input(i_art.id, Analyte=True):
                o_art.udf['Prep Workflow'] = prep_workflow
                o_art.udf['Adapter Type'] = adapter_type
                o_art.put()


if __name__ == "__main__":
    PopulateBatchID().run()
