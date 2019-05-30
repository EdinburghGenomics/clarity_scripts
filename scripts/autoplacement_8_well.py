#!/usr/bin/env python

from EPPs.common import Autoplacement


class Autoplacement8Well(Autoplacement):
    #1 to 1 autoplacement for an 8 well strip tube where the input container uses a "A:1" naming format
    # and the output container uses a "1:1" naming format
    _max_nb_input_containers = 1
    _max_nb_output_containers = 1

    output_plate_layout_rows = ["1", "2", "3", "4", "5", "6", "7", "8"]
    output_plate_layout_columns = ["1"]
    input_plate_layout_rows = ["A", "B", "C", "D", "E", "F", "G", "H"]
    input_plate_layout_columns = ["1"]



if __name__ == '__main__':
    Autoplacement8Well().run()