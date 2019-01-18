#!/usr/bin/env python

from EPPs.common import StepEPP
from pyclarity_lims.entities import Sample, Container

def create_96_well_plate(self,project_name,container_type):
    output_container = Container.create(self.lims, type=self.lims.get_container_types(name='96 well plate')[0])
    output_container.name = self.find_available_container(project_name, container_type)
    output_container.put()
    return output_container

class CreateSamples(StepEPP):
    _use_load_config = False  # prevent the loading of the config
    def _run(self):

        all_inputs= all_inputs(unique=True)
        input_sample=all_inputs[0].samples[0]
        input_project=input_sample.project

        udf_container_type=self.process.udf['Container Type']


        # assemble the plate layout of the output 96 well imp output plate as a list. The rows and columns are also used for looping through the output_dict
        plate96_layout_columns = ['1','2','3','4','5','6','7','8','9','10','11','12']
        plate96_layout_rows = ['A', 'B', 'C', 'D', 'E','F','G','H']
        plate96_layout = []

        for column in plate96_layout_columns:
            for row in plate96_layout_rows:
                plate96_layout.append(row + ":" + column)


        if self.process.udf['Duplicate input samples?']=='No':

        group={}

        number_of_groups=0
        group_counter=1

        while group_counter<=4:
            if self.process.udf['Number in Group '+str(group_counter)]>0:
                group[str(group_counter)]= {
                        'Number':self.process.udf['Number in Group '+str(group_counter)],
                        'Coverage': self.process.udf['Coverage (X) ('+str(group_counter)+')'],
                        'Species': self.process.udf['Species ('+str(group_counter)+')'],
                        'Genome Version': self.process.udf['Genome Version ('+str(group_counter)+')'],
                        'Library Type':self.process.udf['Libray Type'],
                        'fastqMerged or Split?':self.process.udf['fastqMerged or Split?'],
                        'Analysis Type':self.process.udf['Analysis Type'],
                        'User Prepared Library':self.process.udf['User Prepared Library']
                }
                number_of_groups+=1
            group_counter+=1

        sample_counter=1

        samples_to_update=[]

        if self.process.udf['Populate input sample?']=='Yes':
            #populate udfs in input sample
            input_sample.udf['Coverage (X)']=group['1']['Coverage']
            input_sample.udf['Species'] =group['1']['Species']
            input_sample.udf['Genome Version'] = group['1']['Genome Version']
            input_sample.put()

        if self.process.udf['Add new samples to input container?']=='Yes':
            #the first sample already exists so start filling the plate from B:1
            plate96_layout_counter=1
            group_counter=1
            current_container = self.process.all_inputs(unique=True)[0].container

        elif self.process.udf['Add new samples to input container?']=='No':
            plate96_layout_counter=1
            group_counter=1
            current_container = create_container(self,input_project.name,'96 well plate')



        while group_counter<=number_of_groups:

            while sample_counter<group[str(group_counter)]['Number']:
                sample_name=input_project.name+current_container.name+plate96_layout[plate96_layout_counter].replace(":","")
                sample=Sample.create(self.lims, container=current_container, position=plate96_layout[plate96_layout_counter],
                                     name=sample_name,project=input_project)
                sample.udf['Coverage (X)']=group[str(group_counter)]['Coverage']
                sample.udf['Species'] =group[str(group_counter)]['Species']
                sample.udf['Genome Version'] = group[str(group_counter)]['Genome Version']
                samples_to_update.append(sample)

                sample_counter+=1
                plate96_layout_counter+=1

                if plate96_layout_counter%96==0:
                    # Note that tubes exist in LIMS as wells in racks so are always LIMS 96 well plates

                    current_container = Container.create(self.lims,
                                                        type=self.lims.get_container_types(name='96 well plate')[0])
                    current_container.name = self.find_available_container(input_project.name, udf_container_type)
                    # We need the container name to be updated as soon as allocated for find_available_container to work for
                    # the next container.
                    current_container.put()

                    plate96_layout_counter=0

            group_counter+=1
            sample_counter=0




        self.lims.put_batch(samples_to_update)


if __name__ == "__main__":
    CreateSamples().run()
