import random

class Allele(object):
    def __init__(self, name, fitness):
        self.name=name
        self.fitness=fitness


class Individual(object):
    def __init__(self,alleles):
        self.alleles=alleles

    def get_genotype(self):
        genotype=''
        for allele in self.alleles:
            genotype=genotype+allele.name
        return genotype

    def get_fitness(self):
        fitness=1
        for allele in self.alleles:
            fitness=fitness*allele.fitness
        return fitness

allele1=Allele('A','1')
allele2=Allele('a','0.94')


locus_one=[Allele('A',1),Allele('a',0.99)]
locus_two=[Allele('B',1),Allele('b',0.99)]
locus_three=[Allele('C',1),Allele('c',0.99)]

individualX=Individual([locus_one[0],locus_two[0],locus_three[0]])
individualY=Individual([locus_one[1], locus_two[1], locus_three[1]])



def choose_alleles():
    allele_list=[random.choice(locus_one), random.choice(locus_two), random.choice(locus_three)]
    return allele_list

count=0
population=[]

for _ in range(100):
    population.append(Individual(choose_alleles()))
    #print(individual_list[count].get_genotype())
    count = count + 1

#for ind in population:
    #print(ind.get_genotype()+' '+str(ind.get_fitness()))


def get_allele_frequency(allele):
    allele_count=0
    for ind in population:
        if allele in ind.get_genotype():
            allele_count += 1

    allele_frequency=allele_count/len(population)
    return allele_frequency

all_alleles = locus_one+locus_two+locus_three

print('\nPopulation size at generation 0: '+str(len(population)))
print('Allele Frequency at generation 0')
for a in all_alleles:
    print(a.name+' '+ str(get_allele_frequency(a.name)))


def kill_individuals(population):
    for _ in range(10):
        for ind in population:
            #probability=random.random()
            if random.random() > ind.get_fitness():
                population.remove(ind)

#kill_individuals(population)

#print('\nPopulation size after 10 generations: '+str(len(population)))
print('Allele Frequency after 10 generations')
for a in all_alleles:
    print(a.name+' '+ str(get_allele_frequency(a.name)))

def spawn_individuals(population):
    while len(population)<100:
        individual_to_clone=random.choice(population)
        new_individual=Individual(individual_to_clone.alleles)
        population.append(new_individual)
        #population.append(random.choice(population))
    #print(len(population))

#spawn_individuals(population)

def run_generation(number, population, all_alleles):
    count=0
    while count<number:
        print('\nAllele Frequency at generation:'+ str(count))
        for a in all_alleles:
            print(a.name + ' ' + str(get_allele_frequency(a.name)))
        kill_individuals(population)
        spawn_individuals(population)
        count+=1

run_generation(50, population, all_alleles)