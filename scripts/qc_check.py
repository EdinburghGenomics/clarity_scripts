#!/usr/bin/env python

import operator

from EPPs.common import StepEPP


class QCCheck(StepEPP):
    """
    If the step has one output per input then output UDF compared against step UDF with logical operator defined in the
    arguments with a review UDF updated with text specified in the arguments.
    If the step has replicate outputs or if the step has no outputs then the input UDF is compared against the the step UDF (activated with '-ci'
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
        self.passed = self.cmd_args.passed
        self.check_inputs = self.cmd_args.check_inputs


    @staticmethod
    def add_args(argparser):

        # the -n argument can have as many entries as required,
        # if there are spaces within the udfnames and when running locally
        # then they must be enclosed in speech marks " not quotes ' -n "udf name 1" "udf name 2" "udfname 3" BUT
        # use quotes ' when configuring the EPP as speech marks close the bash command
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
        argparser.add_argument('-d', '--passed', type=str, required=False, default='PASSED',
                               help='entries that should go into the output QC UDFs if passes')
        argparser.add_argument('-ci', '--check_inputs', action='store_true',
                               help='set the script to check the input UDF and not outputs',
                               default=False)

    def _compare_true(self, value1, logic_operator, value2):
        """
        Function using getattr and operator to compare the UDF values where getattr is equivalent to the attribute
        e.g. operator.gt(result, value to compare to)
        """
        operators = {
            '>': 'gt',
            '>=': 'ge',
            '==': 'eq',
            '<': 'lt',
            '<=': 'le'
        }
        comparison_method = getattr(operator, operators[logic_operator])
        return comparison_method(value1, value2)

    def _compare_all_artifacts(self, artifacts):
        """For each artifacts provided compare the value in the UDF with the value in the Step UDF.
        Then assign the value in the qc_result to the QC UDF"""
        for art in artifacts:
            if art.name.find("Std")==-1:
                for qc_udf_name in self.qc_udf_names:
                    art.udf[qc_udf_name] = self.passed

                for step_udf_name, result_udf_name, logic_op, qc_udf_name, qc_result in \
                        zip(self.step_udf_names, self.result_udf_names, self.logic_ops, self.qc_udf_names, self.qc_results):
                    if not self._compare_true(art.udf.get(result_udf_name), logic_op, self.process.udf.get(step_udf_name)):
                        art.udf[qc_udf_name] = qc_result

    def _run(self):
        # will update the LIMS using batch for efficiency so need a step variable to populate before the put
        artifacts_to_update = set()

        # we want to update all the outputs that are analytes so will have result UDF values i.e. not files. These are
        # identified as there output-generation-type is "PerInput" which is provided by input_output_maps attribute of
        # process (list of tuples, each tuple is two dictionaries, one for the input and one for the output

        # if -ci argument not present then QC check is between the output UDF and step UDF
        if not self.check_inputs:
            # Will update the LIMS using batch for efficiency so need a step variable to populate before the put
            # Obtaining the output from the input_output maps works for steps where both the output is an analyte
            # or a resultfile
            for input_output in self.process.input_output_maps:
                if input_output[1]['output-generation-type'] == 'PerInput':
                    output = input_output[1]["uri"]  # obtains the output artifact
                    artifacts_to_update.add(output)

        # if -ci argument is present then QC check is between the input UDF and step UDF
        else:
            artifacts_to_update.update(self.process.all_inputs())
        self._compare_all_artifacts(artifacts_to_update)
        self.lims.put_batch(list(artifacts_to_update))


if __name__ == "__main__":
    QCCheck().run()
