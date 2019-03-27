#!/usr/bin/env python

from EPPs.common import Autoplacement


class Autoplacement96well(Autoplacement):
    _max_nb_input_containers = 27

    output_plate_layout_rows = ["A", "B", "C", "D", "E", "F", "G", "H"]
    output_plate_layout_columns = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
    input_plate_layout_columns = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"]
    input_plate_layout_rows = ["A", "B", "C", "D", "E", "F", "G", "H"]


if __name__ == '__main__':
    Autoplacement96well().run()
