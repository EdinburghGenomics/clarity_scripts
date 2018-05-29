import re

class InvalidSequenceCharacter(Exception):
    pass

class InvalidGeneName(Exception):
    pass

class InvalidSpeciesName(Exception):
    pass

class DNARecord(object):
    def __init__(self, sequence, gene_name, species_name):
        self.sequence = sequence
        if re.search(r'[^ATGC]', sequence):
            raise InvalidSequenceCharacter('Sequence cannot contain non-ATGC characters')
        self.gene_name = gene_name
        for letter in gene_name:
            if letter.islower():
                raise InvalidGeneName('Sequence cannot contain lower case letters')
        self.species_name = species_name
        if not re.search(r'[A-Z][a-z]+[ ][a-z]+',species_name):
            raise InvalidSpeciesName('Species name must match the formatting of "Genus species"')

try:
    record1=DNARecord('ARTCGC','BOoB1','Bobus Bbobus')
except InvalidSequenceCharacter:
    print('Sequence cannot have non-ATGC characters')
except InvalidGeneName:
    print('Sequence cannot have lower case letters')
except InvalidSpeciesName:
    print('Species name must have the same format as "Genus species"')


#print(record1.sequence)