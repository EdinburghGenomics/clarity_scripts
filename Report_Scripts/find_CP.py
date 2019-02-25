#!/usr/bin/env python
from EPPs.common import StepEPP
import csv
import sys

class FindCP(StepEPP):
    _use_load_config = False  # prevent the loading of the config
    def _run(self):
        cp_values_to_write=[]
        #print(self.process.input_output_maps)
        input_output_map=self.process.input_output_maps
        for art in input_output_map:
            #print("an art\n")
            #print(art[1])
            if art[1]["output-type"]=="ResultFile":

                row=art[0]["uri"].name,art[0]["uri"].udf["Raw CP"],art[1]["uri"].udf["Raw CP"]
                cp_values_to_write.append(row)
        print(cp_values_to_write)
        with open('CP_report.csv', 'w') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerows(cp_values_to_write)



if __name__ == '__main__':
    sys.exit(FindCP().run())

