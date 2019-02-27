#!/usr/bin/env python

from EPPs.common import step_argparser, StepEPP


class Subtraction(StepEPP):
    """
    Update a volume UDF on the input or output. Argument used to define if input or output UDF updated. Always
    subtracts a step UDF, defined by an argument from a sample UDF, defined by an argument. If the value in the
    step UDF should be added to the sample UDF value then the step UDF can be negative.
    """

    # define init with the udf, operator and result text required
    def __init__(self, argv=None):
        super().__init__(argv)
        self.step_udf_names = self.cmd_args.step_udf_names
        self.sample_udf_names = self.cmd_args.sample_udf_names
        self.inputs = self.cmd.args.input

    @staticmethod
    def add_args(argparser):
        argparser.add_argument('-n', '--step_udf_names', nargs='*',
                   help='step udfs containing the values to be subtracted')
        argparser.add_argument('-t', '--sample_udf_names', nargs='*',
                   help='output/inputs udfs which will be modified')

        argparser.add_argument('-i', '--inputs', action='store_true',
                   help='if present then the input UDFs are updated', default=False)


    def _run(self):

        # we want to update all the outputs that are analytes so will have result UDF values i.e. not files. These are
        # identified as there output-generation-type is "PerInput" which is provided by input_output_maps attribute of
        # process (list of tuples, each tuple is two dictionaries, one for the input and one for the output

        # if -r argument not present then the step UDF is subtracted from each output artifict that is an analyte
        if self.inputs == False:
            # will update the LIMS using batch for efficiency so need a step variable to populate before the put
            outputs_to_update = set()

            for input_output in self.process.input_output_maps:

                if input_output[1]['output-generation-type'] == 'PerInput':

                    output = input_output[1]["uri"]  # obtains the output artifact
                    # assuming that order in each argument list is the same and the number of values in each argument list
                    # is the same then loop through the arguments together using the zip standard function

                    for step_udf_name, sample_udf_name in zip(self.step_udf_names, self.sample_udf_names):
                        # calculate the new sample_udf_name value by subtracting the step_udf_name from the existing
                        # sample_udf_name

                        output.udf[sample_udf_name] = output.udf[sample_udf_name] - self.process.udf[step_udf_name]

                        outputs_to_update.add(output)
            self.lims.put_batch(list(outputs_to_update))

        # if -r argument is present then the step UDF is subtracted from the input artifact
        elif self.inputs == True:
            # will update the LIMS using batch for efficiency so need a step variable to populate before the put

            inputs_to_update = set()
            for input in self.process.all_inputs(unique=True):
                for step_udf_name, sample_udf_name in zip(self.step_udf_names, self.sample_udf_names):
                    # assuming that order in each argument list is the same and the number of values in each argument list
                    # is the same then loop through the arguments together using the zip standard function
                    input.udf[sample_udf_name] = input.udf.get(sample_udf_name) - self.process.udf.get(step_udf_name)
                    inputs_to_update.add(input)
            self.lims.put_batch(list(inputs_to_update))


if __name__ == '__main__':
    Subtraction().run()
