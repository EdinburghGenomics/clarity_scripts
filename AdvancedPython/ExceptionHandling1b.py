import os
import sys

# check for valid filename


try:
    input_file = input('enter filename:\n')
    f = open(input_file)
    dna = f.read().rstrip("\n")
    f.close()
    pieces = input('enter number of pieces:\n')
    pieces = int(pieces)
    piece_length = int(len(dna) / pieces)
    print('piece length is ' + str(piece_length))

except FileNotFoundError:
    sys.exit("File not present")
except ValueError:
    sys.exit('Entry invalid. Please enter an integer.')
except ZeroDivisionError:
    sys.exit('Number of pieces must be greater than zero')
else:
    for start in range(0, len(dna) - piece_length + 1, piece_length):
        print(dna[start:start + piece_length])


