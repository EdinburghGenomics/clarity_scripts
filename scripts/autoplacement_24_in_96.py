#!/usr/bin/env python

from EPPs.common import Autoplacement


# Script for performing autoplacement of samples. If 1 input and 1 output then 1:1 placement. If multiple input plates then
# takes all samples from each plate before next plate Loops through all inputs and assigns them to the next available space
# by column-row in the output plate
class Autoplacement24in96(Autoplacement):

    _max_nb_inputs = 24
    output_plate_layout_columns = ["1", "2", "3"]
    output_plate_layout_rows = ["A", "B", "C", "D", "E", "F", "G", "H"]
    input_plate_layout_columns = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "11", "12"]
    input_plate_layout_rows = ["A", "B", "C", "D", "E", "F", "G", "H"]


if __name__ == '__main__':
    Autoplacement24in96().run()
