#!/usr/bin/env python

from EPPs.common import StepEPP, step_argparser


class CalculateCFPVolumes(StepEPP):
    """
    Calcuate the volume of sample and volume of buffer required based on step UDFs determining a target concentration
    and overall volume. Arguments are used to specify the UDFs involved. Volumes are rounded to 1dp.
    """

    # use arguments to determing
    def __init__(self, step_uri, username, password, target_volume_udf, target_conc_udf, input_conc, input_volume,
                 input_buffer, log_file=None):
        super().__init__(step_uri, username, password, log_file)
        self.target_volume_udf = target_volume_udf
        self.target_conc_udf = target_conc_udf
        self.input_conc = input_conc
        self.input_volume = input_volume
        self.input_buffer = input_buffer

    def _run(self):
        # obtain the target volume and concentration from the step UDFs specified by the arguments
        target_volume = self.process.udf.get(self.target_volume_udf)
        target_concentration = self.process.udf.get(self.target_conc_udf)
        # create the set to hold the inputs to be updated with the output form the calculation
        inputs_to_update = set()

        # obtain the concentration of each input and use that calculate the volume of sample and buffer required
        for input in self.process.all_inputs():
            input.udf[self.input_volume] = round((target_volume * (target_concentration / input.udf.get(self.input_conc))),1)
            input.udf[self.input_buffer] = target_volume - input.udf.get(self.input_volume)
            inputs_to_update.add(input)

        self.lims.put_batch(list(inputs_to_update))


def main():
    # Get the default command line options
    p = step_argparser()
    p.add_argument('-n', '--target_volume_udf', type=str,
                   help='step udf containing the volume of normalised sample to be created')

    p.add_argument('-t', '--target_conc_udf', type=str,
                   help='step udf containing the concentration of the normalised sample')
    p.add_argument('-o', '--input_conc', type=str,
                   help='input UDF containing the sample concentration')
    p.add_argument('-v', '--input_volume', type=str,
                   help='input UDF to be updated with the volume of sample required')
    p.add_argument('-w', '--input_buffer', type=str,
                   help='input UDF to be updtaed with the volume of buffer required')

    # the -n argument can have as many entries as required, if there are spaces within the udfnames and when running locally
    # then they must be enclosed in speech marks " not quotes ' -n "udf name 1" "udf name 2" "udfname 3" BUT use quotes ' when configuring the EPP as speech marks close the
    # bash command e.g.

    # Parse command line options
    args = p.parse_args()

    # Setup the EPP
    action = CalculateCFPVolumes(
        args.step_uri, args.username, args.password, args.target_volume_udf, args.target_conc_udf, args.input_conc,
        args.input_volume, args.input_buffer, args.log_file
    )

    # Run the EPP
    action.run()


if __name__ == "__main__":
    main()
