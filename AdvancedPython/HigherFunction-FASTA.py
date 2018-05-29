FASTA_file=open("sequences.fasta")



def get_FASTA_Sequence(key_word):
    FASTA_lines = []
    for line in open("sequences.fasta"):
        FASTA_lines.append(line)
    sequence_of_interest=[]
    for FASTA_line in FASTA_lines:
        if key_word in FASTA_line:
            sequence_of_interest=sequence_of_interest+[FASTA_line]
            index_position=FASTA_lines.index(FASTA_line)
            sequence_of_interest=sequence_of_interest+[FASTA_lines[index_position+1]]
    #print(sequence_of_interest)
    return sequence_of_interest

def fix_upper(sequence):
    return sequence.upper()

def fix_unknown(sequence):
    unknown_removed_list=list(filter(lambda s :s !='N', sequence))
    unknown_removed=''.join(unknown_removed_list)
    print(unknown_removed)
    return unknown_removed

def replace_space(h):
    if h == " ":
        return "_"
    else:
        return h

def fix_spaces(header):
    spaces_fixed_list=list(map(replace_space, header))
    spaces_fixed=''.join(spaces_fixed_list)
    return spaces_fixed

def fix_spaceholder(header):
    return header

def fix_truncate(header):
    return header[:10]

def fix_append(header):

get_FASTA_Sequence('lower')

#print(fix_upper(get_FASTA_Sequence('lower')[1]))



def modify_FASTA(input_filename,output_filename,fix_sequence, fix_header,key_word):
    sequence_of_interest=get_FASTA_Sequence(key_word)
    sequence_of_interest[0]=str(fix_header(sequence_of_interest[0]))
    sequence_of_interest[1]=fix_sequence(sequence_of_interest[1])
    output_FASTA=open(output_filename,'w')
    for line in sequence_of_interest:
        output_FASTA.write(line)
    output_FASTA.close()
    return sequence_of_interest

print(modify_FASTA('sequences.fasta','output.fasta',fix_unknown, fix_truncate,'truncated'))