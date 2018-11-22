#!/usr/bin/env python

import operator

from EPPs.common import StepEPP


# create a function using getattr and operator to compare the UDF values where getattr is equivalent to the attribute
#  e.g. operator.gt(result, value to compare to)
def ComparisonMethod(result, logic_op, step_udf_value):
    operators = {
        '>': 'gt',
        '>=': 'ge',
        '==': 'eq',
        '<': 'lt',
        '<=': 'le'
    }

    comparison_method = getattr(operator, operators[logic_op])
    return comparison_method(result, step_udf_value)


class QCCheck(StepEPP):
    """
    If the step has one output per input then output UDF compared against step UDF with logical operator defined in the
    arguments with a review UDF updated with text specified in the arguments.
    If the step has replicate outputs then the input UDF is compared against the the step UDF (activated with '-r'
    argument.Use logic ops as the argument defined operators to distinguish from
    the use of the operator library
    """
    _use_load_config = False  # prevent the loading of the config file

    def __init__(self, argv=None):
        super().__init__(argv)
        self.step_udf_names = self.cmd_args.step_udf_names
        self.result_udf_names = self.cmd_args.result_udf_names
        self.logic_ops = self.cmd_args.logic_ops
        self.qc_udf_names = self.cmd_args.qc_udf_names
        self.qc_results = self.cmd_args.qc_results
        self.replicates = self.cmd_args.replicates

    @staticmethod
    def add_args(argparser):

        # the -n argument can have as many entries as required, if there are spaces within the udfnames and when running locally
        # then they must be enclosed in speech marks " not quotes ' -n "udf name 1" "udf name 2" "udfname 3" BUT use quotes ' when configuring the EPP as speech marks close the
        # bash command
        argparser.add_argument(
            '-n', '--step_udf_names', nargs='*', help='step udfs against which values will be compared')
        argparser.add_argument('-t', '--result_udf_names', nargs='*',
                               help='output/inputs udfs which will be compared against step UDFs')
        argparser.add_argument('-o', '--logic_ops', nargs='*',
                               help='logical operators for comparing output/input UDFs with step UDFs')
        argparser.add_argument('-v', '--qc_udf_names', nargs='*',
                               help='output/input  QC udfs that should be updated as a result of the comparison')
        argparser.add_argument('-w', '--qc_results', nargs='*',
                               help='entries that should go into the output QC UDFs if a fail')
        argparser.add_argument('-r', '--replicates', action='store_true',
                               help='set the script to check the input UDF and not individual replicates',
                               default=False)

    def _run(self):

        # we want to update all the outputs that are analytes so will have result UDF values i.e. not files. These are
        # identified as there output-generation-type is "PerInput" which is provided by input_output_maps attribute of
        # process (list of tuples, each tuple is two dictionaries, one for the input and one for the output

        # if -r argument not present then QC check is between the output UDF and step UDF
        if self.replicates is False:
            # will update the LIMS using batch for efficiency so need a step variable to populate before the put
            outputs_to_update = set()

            for input_output in self.process.input_output_maps:

                if input_output[1]['output-generation-type'] == 'PerInput':

                    output = input_output[1]["uri"]  # obtains the output artifact
                    # assuming that order in each argument list is the same and the number of values in each argument list
                    # is the same then loop through the arguments together using the zip standard function
                    for step_udf_name, result_udf_name, logic_op, qc_udf_name, qc_result in zip(self.step_udf_names,
                                                                                                self.result_udf_names,
                                                                                                self.logic_ops,
                                                                                                self.qc_udf_names,
                                                                                                self.qc_results):
                        # check to see if the output result UDF value meets the criteria of the operator when compared to
                        # the step UDF. Also don't want to update the qc UDF if it has already been set to fail for a
                        # previous check

                        if ComparisonMethod(output.udf.get(result_udf_name), logic_op,
                                            self.process.udf.get(step_udf_name)) == True and \
                                str(output.udf.get(qc_udf_name)).find('FAIL') == -1:
                            output.udf[qc_udf_name] = 'PASS'
                            outputs_to_update.add(output)
                        elif ComparisonMethod(output.udf.get(result_udf_name), logic_op,
                                              self.process.udf.get(step_udf_name)) == False:
                            output.udf[qc_udf_name] = qc_result
                            outputs_to_update.add(output)

                self.lims.put_batch(list(outputs_to_update))

        # if -r argument is present then QC check is between the input UDF and step UDF
        elif self.replicates == True:
            # will update the LIMS using batch for efficiency so need a step variable to populate before the put
            inputs_to_update = set()
            for input in self.process.all_inputs():
                for step_udf_name, result_udf_name, logic_op, qc_udf_name, qc_result in zip(self.step_udf_names,
                                                                                            self.result_udf_names,
                                                                                            self.logic_ops,
                                                                                            self.qc_udf_names,
                                                                                            self.qc_results):
                    # check to see if the input result UDF value meets the criteria of the operator when compared to
                    # the step UDF. Also don't want to update the qc UDF if it has already been set to fail for a
                    # previous check. Ignore samples that do not have results.

                    if input.udf.get(result_udf_name) and ComparisonMethod(input.udf.get(result_udf_name), logic_op,
                                                                           self.process.udf.get(
                                                                               step_udf_name)) == True and \
                            str(input.udf.get(qc_udf_name)).find('FAIL') == -1:
                        input.udf[qc_udf_name] = 'PASS'
                        inputs_to_update.add(input)
                    elif input.udf.get(result_udf_name) and ComparisonMethod(input.udf.get(result_udf_name), logic_op,
                                                                             self.process.udf.get(
                                                                                 step_udf_name)) == False:
                        input.udf[qc_udf_name] = qc_result
                        inputs_to_update.add(input)
            self.lims.put_batch(list(inputs_to_update))


if __name__ == "__main__":
    QCCheck().run()
