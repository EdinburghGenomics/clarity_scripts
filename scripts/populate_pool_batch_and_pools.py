#!/usr/bin/env python
from datetime import date

import math

from EPPs.common import StepEPP, InvalidStepError


class PopulatePoolBatchPools(StepEPP):
    # populate the pool ids with format YY-MM-DD_PDP_Pool#{1-9}{1,3} where {1-9}{1,3} is the next available number for
    # that date.
    # populate the pool batch ids with format YY-MM-DD_PDP_Batch#{1-9}{1,3} where {1-9}{1,3} is the next available number for
    # that date.
    # populate the output artifact with the prep workflow and adapter type of the input
    _max_nb_output_containers = 1

    def calculate_NTP_volume(self, pool_name):
        inputs = self.process.step.pools.pooled_inputs[pool_name][1]

        # obtain the Remaing Yield value from the submitted sample for each in put and find the maximum value
        # the volume of NTP is based on all libraries in the pool gaining the same amount of yield as required by
        # the library that requires the largest (maximum) yield i.e. all libraries will have the same volume of NTP to
        # help minimise the problem uncertain sequencing yield caused by unbalanced pools
        max_remaining_yield = max([input.samples[0].udf['Remaining Yield (Gb)'] for input in inputs])

        # find the total amount of data that the pool will need to generate for all libraries combined
        total_remaining_yield = int(max_remaining_yield) * len(inputs)

        # find the total volume of library (NTP) that will be required from all libraries combined assuming 10 ul of pool
        # is added to each CST well. 0.083 is a constant representing the amount of NTP required to generate 1 Gb of
        # data in a balanced pool on one lane of a HiSeqX flowcell
        total_volume_of_ntp_for_yield = total_remaining_yield * 0.083

        #find the number of lanes required, assuming that 10 of NTP is used in each CST well and only whole wells can
        #be used
        number_of_lanes = math.ceil(total_volume_of_ntp_for_yield / 10)#rounds up

        #find the total volume ntp that is required to fill all required lanes and provide a dead volume of 5 ul
        total_volume_of_ntp = (number_of_lanes*10)+5

        #volume of library (ntp) per sample is the total volume of ntp divided by the number of libraries in the pool as
        #equal amounts of each library is added to the pool
        volume_ntp_per_library = total_volume_of_ntp/len(inputs)
        if volume_ntp_per_library<2:
            raise InvalidStepError('NTP Volume (uL) cannot be less than 2. NTP Volume (uL) for libraries in %s is '
                                   '%s' %(pool_name,volume_ntp_per_library))
        return [volume_ntp_per_library,number_of_lanes]

    def create_pool_batch_id(self):
        today = str(date.today())
        name_template = today + '_PDP_Batch#%d'
        # find next available batch id and use range limit to prevent infinite loop
        for batch_count in range(1, 999):
            new_batch_name = name_template % batch_count
            if not self.lims.get_containers(name=new_batch_name):
                return new_batch_name
        raise InvalidStepError('Cannot allocate more than 999 pool batch IDs with date %s' % today)

    def create_pool_id(self):
        today = str(date.today())
        name_template = today + '_PDP_Pool#%d'

        # find next available batch id and use range limit to prevent infinite loop
        for pool_count in range(1, 999):
            new_pool_name = name_template % pool_count

            if not self.lims.get_artifacts(name=new_pool_name):
                return new_pool_name
        raise InvalidStepError('Cannot allocate more than 999 pool IDs with date %s' % today)

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
            original_output_name = o_art.name
            o_art.name = self.create_pool_id()

            o_art.udf['Prep Workflow'] = prep_workflow
            o_art.udf['Adapter Type'] = adapter_type
            o_art.udf['NTP Volume (uL)'],o_art.udf['Number of Lanes'] = self.calculate_NTP_volume(original_output_name)
            o_art.put()


if __name__ == '__main__':
    PopulatePoolBatchPools().run()
