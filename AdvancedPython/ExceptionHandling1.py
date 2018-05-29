import os
import sys

# check for valid filename

input_file = input('enter filename:\n')
try:
    f = open(input_file)
    #if not os.path.isfile(input_file):
    #    sys.exit('not a valid filename')
except FileNotFoundError:
    sys.exit("File not present")
else:
    dna = f.read().rstrip("\n")
    f.close()

pieces = input('enter number of pieces:\n')

# check for valid number
try:
    pieces = int(pieces)

except ValueError:
    sys.exit('Entry invalid. Please enter an integer.')

# check that number is not zero or negative
try:
    piece_length = int(len(dna) / pieces)
except ZeroDivisionError:
    sys.exit('Number of pieces must be greater than zero')

# do the processing
print('piece length is ' + str(piece_length))
for start in range(0, len(dna) - piece_length + 1, piece_length):
    print(dna[start:start + piece_length])