#!/usr/bin/env python

import operator

from EPPs.common import step_argparser, StepEPP


class QCCheck(StepEPP):
    """
    Perform a QC check on an output UDF compared to a step udf using script arguments to define which output UDF and
    step UDF will be compared, which operator will be used to compare them, which output UDF will be updated with a
    result and what will be added as the result. Use logic ops as the argument defined operators to distinguish from
    the use of the operator library
    """

    # define init with the udf, operator and result text required
    def __init__(self, step_uri, username, password, step_udf_names, result_udf_names, logic_ops, qc_udf_names,
                 qc_results,
                 log_file=None):
        super().__init__(step_uri, username, password, log_file)
        self.step_udf_names = step_udf_names
        self.result_udf_names = result_udf_names
        self.logic_ops = ops
        self.qc_udf_names = qc_udf_names
        self.qc_results = qc_results

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

    def _run(self):
        #find all the outputs in the step
        all_outputs = self.process.all_outputs()
        #will update the LIMS using batch for efficiency so need a step variable to populate before the put
        outputs_to_update = set()
        #we want to update all the outputs that are analytes so will have result UDF values i.e. not files
        for output in all_outputs:
            if output.type == 'Analyte':
                #assuming that order in each argument list is the same and the number of values in each argument list
                #is the same then loop through the arguments together using the zip standard function
                for step_udf_name, result_udf_name, logic_op, qc_udf_name, qc_result in zip(self.step_udf_names,
                                                                                            self.result_udf_names,
                                                                                            self.logic_ops,
                                                                                            self.qc_udf_names,
                                                                                            self.qc_results):
                    #check to see if the output result UDF value meets the criteria of the operator when compared to
                    #the step UDF. Also don't want to update the qc UDF if it has already been set to fail for a
                    #previous check
                    if ComparisonMethod(output.udf.get[result_udf_name], logic_op,
                                        self.process.udf.get[step_udf_name]) and \
                            'FAIL' not in output.udf[qc_udf_name]:
                        output.udf[qc_udf_name] = qc_result
                        outputs_to_update.add(output)

        self.lims.put_batch(list(outputs_to_update))


def main():
    # Get the default command line options
    p = step_argparser()
    p.add_argument('-n', '--step_udf_names', nargs='*', help='step udfs against which output values will be compared')
    p.add_argument('-t', '--result_udf_names', nargs='*', help='output udfs which will be compared against step UDFs')
    p.add_argument('-o', '--logic_ops', nargs='*', help='logical operators for comparing output UDFs with step UDFs')
    p.add_argument('-v', '--qc_udf_names', nargs='*',
                   help='output udfs that should be updated as a result of the comparison')
    p.add_argument('-w', '--qc_results', nargs='*',
                   help='output udfs that should be updated as a result of the comparison')

    # the -n argument can have as many entries as required, if there are spaces within the udfnames and when running locally
    # then they must be enclosed in speech marks " not quotes ' -n "udf name 1" "udf name 2" "udfname 3" BUT use quotes ' when configuring the EPP as speech marks close the
    # bash command e.g.

    # Parse command line options
    args = p.parse_args()

    # Setup the EPP
    action = CheckStepUDFs(
        args.step_uri, args.username, args.password, args.result_udf_names, args.logic_ops, args.qc_udf_names,
        args.qc_results, args.log_file,
    )

    # Run the EPP
    action.run()


if __name__ == "__main__":
    main()
