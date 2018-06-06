#!/usr/bin/env python
from EPPs.common import StepEPP, step_argparser
import csv

class GenerateHamiltonInputUPL(StepEPP):
    """"Generate a CSV containing the necessary information to batch up ot 9 User Prepared Library receipt
    into one DCT plate. Requires input and output plate containers and well positions from LIMS. Volume to be pipetted
    is taken from the step UDF "DNA Volume (uL)"""

    def _run(self):
        all_inputs = self.process.all_inputs()
        csv_array=[]
        csv_column_headers=['Input Plate','Input Well','Output Plate','Output Well','DNA Volume','TE Volume']
        csv_array.append(csv_column_headers)


        for input in all_inputs:
            if input.type=='Analyte':
                output = self.process.outputs_per_input(input.id,Analyte=True)
                if output[0].type =='Analyte':
                    output_container=output[0].container.name
                    output_well=output[0].location[1]


                csv_line=[input.container.name,input.location[1],output_container,output_well,self.process.udf['DNA Volume (uL)'],'0']
                csv_array.append(csv_line)
        print(csv_array)

        with open('hamilton_input.csv','w') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerows(csv_array)
        csvFile.close()

def main():
    p = step_argparser()
    args = p.parse_args()


    action = GenerateHamiltonInputUPL(args.step_uri, args.username, args.password, args.log_file)
    action.run()


if __name__ == '__main__':
    main()