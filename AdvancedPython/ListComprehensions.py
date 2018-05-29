lines= []
for line in open('blast_result.txt'):
    lines.append(line)

hit_lines=[line for line in lines if not line.startswith('#')]




def get_mismatch(line):
    return int(line.split('\t')[4])


def low_mismatch(line):
     return get_mismatch(line)<20

#print("Number of lines mismatch where <20 = "+str(len(list(filter(low_mismatch, hit_lines)))))

mismatch_less_20= [line for line in hit_lines if int(line.split('\t')[4]) < 20]

print("Number of lines where mismatch is <20 = "+str(len(mismatch_less_20)))

def get_subject(line):
    return line.split('\t')[1]

def get_identical(line):
    return line.split('\t')[2]

sort_by_identical=list(sorted(hit_lines, key=get_identical))

#print(type(sort_by_identical))

list_of_ten=[line.split('\t')[1] for line in sort_by_identical[:10]]


print('\nList of 10 Subject names with lowest percentage of identical positions:')
count=0

while count<10:
    print(list_of_ten[count])
    count+=1

def get_COX1(line):
    return "COX1" in line.split('\t')[1]

def start_proportion(line):
    return int(line.split('\t')[6])/int(line.split('\t')[3])

#filtered_by_COX1 = filter(get_COX1,hit_lines)

filtered_by_COX1 = [int(line.split('\t')[6])/int(line.split('\t')[3]) for line in hit_lines if 'COX1' in line]

print('\nStart position as proportion of length for hits where COX1 is in subject name:')


for line in filtered_by_COX1:
    print(line)






