#!/usr/bin/env python
from EPPs.common import StepEPP, InvalidStepError


class CheckPlatesLibrariesIndexes(StepEPP):
    """if multiple library types or adapter (reagent) types present then generates an error. Assumes that inputs can be pools
    so may have multiple types"""
    _max_nb_input_containers = 10

    def check_index_and_libraries(self):
        #ensures step cannot start if >10 plates or multiple adapter types or multiple libray prep workflow
        # types present
        library_types=set()
        adapter_type_categories=set()
        for art in self.artifacts:

            for sample in art.samples:
                try:
                    library_types.add(sample.udf['Prep Workflow'])
                except KeyError:
                    raise InvalidStepError('Prep Workflow missing from artifact %s' % art.name)



            #create an instance of the reagent type by obtaining the reagent type with get reagent type using
            # the reagent label as the name
            # Note: each individual index is a "reagent_type", each index belongs to a group called a "category"
            #now that we have an instance of the reagent_type we can obtain the class variable "category".
            for reagent_label in art.reagent_labels:
                adapter_type_categories.add(self.lims.get_reagent_types(name=reagent_label)[0].category)

        if len(library_types) > 1:
            raise InvalidStepError('Multiple library types (Prep Workflow) present in step. Only 1 permitted.')

        if len(adapter_type_categories) > 1:
            raise InvalidStepError('Multiple index types present in step. Only 1 permitted.')

    def _run(self):
        self.check_index_and_libraries()

if __name__ == "__main__":
    CheckPlatesLibrariesIndexes().run()