#!/usr/bin/env python

from EPPs.common import Autoplacement


class Autoplacement24in96(Autoplacement):
    _max_nb_inputs = 24
    output_plate_layout_columns = ["1", "2", "3"]
    output_plate_layout_rows = ["A", "B", "C", "D", "E", "F", "G", "H"]
    input_plate_layout_columns = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "11", "12"]
    input_plate_layout_rows = ["A", "B", "C", "D", "E", "F", "G", "H"]


if __name__ == '__main__':
    Autoplacement24in96().run()
