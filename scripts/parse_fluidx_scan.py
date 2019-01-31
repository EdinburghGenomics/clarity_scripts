#!/usr/bin/env python
import csv
import platform

from EPPs.common import StepEPP



class ParseFluidXScan(StepEPP):

    # additional argument required to obtain the file location for newly create manifest in the LIMS step
    def __init__(self, argv=None):
        super().__init__(argv)
        self.fluidx_scan = self.cmd_args.fluidx_scan

    @staticmethod
    def add_args(argparser):
        argparser.add_argument(
            '-x', '--fluidx_scan', type=str, required=True, help='Sample manifest generated by the LIMS'
        )

    def _run(self):



        # find the MS Excel manifest
        for output in self.process.all_outputs(unique=True):
            if output.id == self.fluidx_scan:
                #LOCAL TESTING location = output.files[0].original_location
                location = output.files[0].content_location.split('sftp://' + platform.node())[1]
                with open(location,mode='r') as fluidx_scan_file:
                    fluidx_scan_list = list(csv.reader(fluidx_scan_file))

        all_inputs=self.process.all_inputs(unique=True)



        #check the number of samples in the step matches the number of tubes the fluidx scanner counted
        if not len(all_inputs) == int(fluidx_scan_list[1][1]):
            raise ValueError('The number of samples %s in the steps does not match the number of tubes scanned %s'
                             % (len(all_inputs), fluidx_scan_list[1][1]))

        sample_dict={}

        for artifact in all_inputs:
            sample_dict[artifact.location[0].name+artifact.location[1].replace(':','')]=artifact.samples[0]

        sample_list=[]

        for line in fluidx_scan_list:
            if not line[0] == 'Rack ID' and not line[0] == 'Tube Count':
                if line[0]+line[1] in sample_dict:
                    sample_dict[line[0]+line[1]].udf['2D Barcode'] = line[2]
                    sample_list.append(sample_dict[line[0] + line[1]])

        self.lims.put_batch(sample_list)


if __name__ == '__main__':
    ParseFluidXScan().run()