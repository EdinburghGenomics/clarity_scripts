import sys
from EPPs.common import StepEPP


class AutoplacementMakeCFP(StepEPP):
    _use_load_config = False  # prevent the loading of the config

    def __init__(self, argv=None):
        super().__init__(argv)

    def _run(self):

        all_inputs=self.process.all_inputs(unique=True)
        if len(all_inputs)>24:
            print("Maximum number of inputs is 24. %s inputs present in step" %(len(all_inputs)))
            sys.exit(1)

        plate_layout_rows=["1","2","3"]
        plate_layout_columns=["A","B","C","D","E","F","G","H"]
        plate_layout=[]

        for row in plate_layout_rows:
            for column in plate_layout_columns:
                plate_layout.append(column+":"+row)

        well_counter=0



        outputs_to_update=set()

        for input in all_inputs:
            print(input)
            output= self.process.input_output_maps
            print(output)
            #output[0].location = plate_layout[well_counter]

            #outputs_to_update.add(output)
            #well_counter += 1

        #self.lims.put_batch(list(outputs_to_update))

if __name__ == '__main__':
    AutoplacementMakeCFP().run()
