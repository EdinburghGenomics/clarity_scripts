#!/usr/bin/env python
import sys

from EPPs.common import StepEPP, InvalidStepError


class QPCRDilutionCalculation(StepEPP):
    """
    The purpose of this script is to calculate the required volume of buffer to be added to a set volume of a DCT sample
    to achieve a target concentration. The dilution will only occur if the DCT sample concentration is above a threshold
     concentration. The script will also populate the output udfs of the step with a number input artifact udfs that
     will get overwritten when the QPCR is re-run. This means the values are permanently stored and can be retried in
      future.
    """

    def _run(self):
        input_artifacts = self.process.all_inputs(unique=True)
        step_udfs = self.process.udf

        # create the set to hold the inputs to be updated with the output form the calculation
        artifacts_to_update = set()

        for input_art in input_artifacts:

            output = self.process.outputs_per_input(input_art, ResultFile=True)[0]
            udf_names = ['Adjusted Conc. (nM)', 'Ave. Conc. (nM)', 'Original Conc. (nM)', '%CV']

            if None not in udf_names:
                for name in udf_names:
                    output.udf[name] = input_art.udf[name]
            else:
                raise InvalidStepError('UDF population failed due to missing input value in %s' % udf_names)

            if int(input_art.udf['Adjusted Conc. (nM)']) > int(step_udfs['Threshold Concentration (nM)']):
                try:
                    total_volume = int(step_udfs['DCT Volume (ul)']) * (
                            int(input_art.udf['Adjusted Conc. (nM)']) / int(step_udfs['Target Concentration (nM)']))
                    output.udf['RSB Volume (ul)'] = str(round(total_volume - int(step_udfs['DCT Volume (ul)'])))
                except:
                    raise InvalidStepError('Missing value. Check that step UDFs (Adjusted Conc. (nM) and Target '
                                           'Concentration (nM)) are populated')
            else:

                output.udf['RSB Volume (ul)'] = '0'



            artifacts_to_update.add(output)

        #update all output artifacts with input artifact values and new RSB volumes
        self.lims.put_batch(list(artifacts_to_update))


if __name__ == '__main__':
    sys.exit(QPCRDilutionCalculation().run())
