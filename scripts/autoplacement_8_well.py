#!/usr/bin/env python

from EPPs.common import Autoplacement


class Autoplacement8Well(Autoplacement):
    #autoplacement for an 8 well strip tube
    _max_nb_input_containers = 1
    _max_nb_output_containers = 1

    output_plate_layout_rows = ["1", "2", "3", "4", "5", "6", "7", "8"]
    output_plate_layout_columns = ["1"]
    input_plate_layout_rows = ["1", "2", "3", "4", "5", "6", "7", "8"]
    input_plate_layout_columns = ["1"]



if __name__ == '__main__':
    Autoplacement8Well().run()