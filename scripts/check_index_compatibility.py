#!/usr/bin/env python
import operator
import sys
from itertools import combinations

from EPPs.common import StepEPP, InvalidStepError


class CheckIndexCompatibility(StepEPP):
    '''Checks the index compatibility within pools created in the step and populate artifact udfs with the Hamming
    distances separately for both the I7 and I5 indexes.'''

    def populate_output_udfs(selfs, hamming_distances, outputs_to_put, output):
        output.udf['Min I7 Hamming Distance'] = str(hamming_distances[0])
        output.udf['Min I5 Hamming Distance'] = str(hamming_distances[1])
        outputs_to_put.append(output)



    def qc_check_hamming_distances(self, hamming_distances, output):
        '''Compares the Hamming distances of the indexes against the thresholds defined by step UDFs.
         If for a "Single Read" sequencing run then there must be a difference in the I7 index. If for a "Dual Read"
        sequencing run then the difference can be in either the I7 or I5 (or both).'''
        if self.process.udf['Compatibility Check'] == 'Single Read':
            if hamming_distances[0] < int(self.process.udf['Single Read Minimum Hamming Distance']):
                raise InvalidStepError('Indexes not compatible within pool %s' % output.name)
        elif self.process.udf['Compatibility Check'] == 'Dual Read':
            if hamming_distances[0] + hamming_distances[1] < int(
                    self.process.udf['Dual Read Minimum Hamming Distance']):
                raise InvalidStepError('Indexes not compatible within pool %s' % output.name)

    def calculate_hamming_distances(self, indexes_list):
        ''' Calculates the minimum I7 and I5 Hamming distances for the indexes in the pool. Performs a pairwise comparison
        of all possible I7 pairs and all possible I5 pairs. Measures the length of the indexes in each pair and only
        compares a length from 0 to the length of the shortest index.'''
        hamming_distance_i7_list = []
        hamming_distance_i5_list = []
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
        return [hamming_distance_i7_min, hamming_distance_i5_min]

    def get_indexes_list(self, inputs):
        # generate a list of indexes from all of the inputs for the pool
        indexes_list = []
        for input in inputs:
            index_pair = input.reagent_labels[0].split('(')[1]
            index_pair = index_pair.split(')')[0]
            indexes_list.append(index_pair)
        return indexes_list

    def _run(self):

        outputs_to_put = []
        # for each output pool find all the input artifacts, obtain their indexes and calculate the minimum Hamming
         #distances between I7 and I5 indexes

        for output in self.output_artifacts:

            #find the output pools i.e. outputs with type 'Analyte'
            if output.type == 'Analyte':
                # find all the input_output maps for the output artifact
                inputs_outputs = [io for io in self.process.input_output_maps if io[1]['limsid'] == output.id]

                inputs = [io[0]['uri'] for io in inputs_outputs]

                indexes_list = self.get_indexes_list(inputs)

                hamming_distances = self.calculate_hamming_distances(indexes_list)
                self.qc_check_hamming_distances(hamming_distances, output)
                self.populate_output_udfs(hamming_distances, outputs_to_put, output)

        self.lims.put_batch(outputs_to_put)


if __name__ == '__main__':
    sys.exit(CheckIndexCompatibility().run())
