#!/usr/bin/env python
from EPPs.common import StepEPP, InvalidStepError


class CheckPlatesLibrariesAdapters(StepEPP):
    _max_nb_input_containers = 10

    def check_adapters_and_libraries(self):
        library_types=set()
        adapter_type_categories=set()
        for art in self.artifacts:

            try:
                library_types.add(art.samples[0].udf.get('Prep Workflow'))
            except:
                raise InvalidStepError('Prep Workflow missing from artifact %s' % art.name)

            if len(art.reagent_labels)>1:

                raise InvalidStepError('Multiple reagent labels present (adapters) on artifact %s. Only 1 permitted' % art.name)
            else:
                #create an instance of the reagent type by obtaining the reagent type with get reagent type using
                # the reagent label as the name

                reagent_type= self.lims.get_reagent_types(name=art.reagent_labels[0])[0]

                #now that we have an instance of the reagent_type we can obtain the class variable "category"
                adapter_type_categories.add(reagent_type.category)

        if len(library_types) > 1:
            raise InvalidStepError('Multiple library types (Prep Workflow) present in step. Only 1 permitted')

        if len(adapter_type_categories) > 1:
            raise InvalidStepError('Multiple adapter types present in step. Only 1 permitted.')

    def _run(self):
        self.check_adapters_and_libraries()

if __name__ == "__main__":
    CheckPlatesLibrariesAdapters().run()