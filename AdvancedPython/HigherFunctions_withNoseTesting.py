from nose.tools import assert_true

lines= []
for line in open('blast_result2.txt'):
    lines.append(line)


def comment_filter(line):
    return not line.startswith('#')



hit_lines=list(filter(comment_filter,lines))
assert_true(len(list(filter(comment_filter,lines)))>0)
#print(list(hit_lines))


def get_mismatch(line):
    return int(line.split('\t')[4])


def low_mismatch(line):
     return get_mismatch(line)<20

print("Number of lines mismatch where <20 = "+str(len(list(filter(low_mismatch, hit_lines)))))

def get_subject(line):
    return line.split('\t')[1]

def get_identical(line):
    return line.split('\t')[2]

sort_by_identical=list(sorted(hit_lines, key=get_identical))


#print(list(map(get_subject,sort_by_identical))[0:9])

print('\nList of 10 Subject names with lowest percentage of identical positions:')
count=0

while count<10:
    print(str(list(map(get_subject, sort_by_identical))[count])+" "+ str(list(map(get_identical, sort_by_identical))[count]))
    count+=1

def get_COX1(line):
    return "COX1" in line.split('\t')[1]

def start_proportion(line):
    return int(line.split('\t')[6])/int(line.split('\t')[3])

filtered_by_COX1 = filter(get_COX1,hit_lines)
#print(list(map(start_proportion,filtered_by_COX1)))

proportion_list=list(map(start_proportion, filter(get_COX1, hit_lines)))
print('\nStart position as proportion of length for hits where COX1 is in subject name:')
for proportion in proportion_list:
    print(proportion)

#print(list(map(start_proportion,filter(get_COX1,hit_lines))))

assert_true(len(list(filter(comment_filter,lines)))>0)


