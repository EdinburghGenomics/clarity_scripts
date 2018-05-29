def generate_kmers_rec(k):
    #print("generating kmers of length " + str(k))
    # if k is one, then the result is all one-base strings
    if k == 1:
        #print("returning " + str(['A', 'T', 'G', 'C']))
        return ['A', 'T', 'G', 'C']

        # if k is bigger than one...
    else:
        result = []

        # ...get a list of all kmers which are one base shorter...
        shorter_seqs = generate_kmers_rec(k - 1)
        for seq in shorter_seqs:

            # ...and append each of the four possible bases
            for base in ['A', 'T', 'G', 'C']:
                result.append(seq + base)

        return result




print(generate_kmers_rec(3))