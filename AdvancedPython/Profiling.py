import random

# create a random dna sequence
@profile
def random_dna(length):
    return "".join([random.choice(['A','T','G','C']) for _ in range(length)])

@profile
def random_motifs(length, number):
    return [random_dna(4) for _ in range(100)]



@profile
def classify_chunks(dna, motifs):
# standard kmer counting code to identify frequent chunks
    frequent_chunks = []

    for start in range(len(dna) - 3):
        chunk = dna[start:start + 4]
        if dna.count(chunk) > 50:
            frequent_chunks.append(chunk)

    # now check each chunk to see if it's in the list of motifs
    for chunk in frequent_chunks:
        if chunk in motifs:
            print(chunk + " is frequent and interesting")
        else:
            print(chunk + " is frequent but not interesting")

print(classify_chunks(random_dna(10000),random_motifs(4,100)))