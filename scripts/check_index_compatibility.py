#!/usr/bin/env python
import operator
import sys
from itertools import combinations

from EPPs.common import StepEPP, InvalidStepError


class CheckIndexCompatibility(StepEPP):

    def run(self):
        indexes_list = []
        hamming_distance_i7_list = []
        hamming_distance_i5_list = []
        outputs_to_put = []

        for output in self.output_artifacts:
            # find all the input_output maps for the output artifact

            if output.type == 'Analyte':
                inputs_outputs = [io for io in self.process.input_output_maps if io[1]['limsid'] == output.id]

                inputs = [io[0]['uri'] for io in inputs_outputs]

                # obtain the indexes (reagent labels) for each input, extract the I7 and I5 sequences then calculate the
                # hamming distance for both I7 and I5

                for input in inputs:
                    index_pair = input.reagent_labels[0].split('(')[1]
                    index_pair = index_pair.split(')')[0]
                    indexes_list.append(index_pair)

                for indexes in combinations(indexes_list, 2):
                    ne = operator.ne
                    index_0_i7, index_0_i5 = indexes[0].split('-')
                    index_1_i7, index_1_i5 = indexes[1].split('-')
                    # obtain length of smallest index in the i7 comparison (although often will be standard)
                    length = min(len(index_0_i7), len(index_1_i7))
                    # calculate the hamming distance for i7
                    hamming_distance_i7_list.append(sum(map(ne, index_0_i7[:length], index_1_i7[:length])))
                    # obtain length of smallest index in the i7 comparison (although often will be standard)

                    length = min(len(index_0_i5), len(index_1_i5))
                    # calculate the hamming distance for i5
                    hamming_distance_i5_list.append(sum(map(ne, index_0_i5[:length], index_1_i5[:length])))

                hamming_distance_i7_min = min(hamming_distance_i7_list)
                hamming_distance_i5_min = min(hamming_distance_i5_list)

                output.udf['Min I7 Hamming Distance'] = str(hamming_distance_i7_min)
                output.udf['Min I5 Hamming Distance'] = str(hamming_distance_i5_min)
                outputs_to_put.append(output)

                if output.location[0].type.name == 'Single Read PDP Batch ID':
                    if hamming_distance_i7_min < int(self.process.udf['Single Read Minimum Hamming Distance']):
                        raise InvalidStepError('Indexes not compatible within pool %s' % output.name)
                elif output.location[0].type.name == 'Dual Read PDP Batch ID':
                    if hamming_distance_i7_min + hamming_distance_i5_min < int(
                        self.process.udf['Dual Read Minimum Hamming Distance']):
                        raise InvalidStepError('Indexes not compatible within pool %s' % output.name)

        self.lims.put_batch(outputs_to_put)


if __name__ == '__main__':
    sys.exit(CheckIndexCompatibility().run())
