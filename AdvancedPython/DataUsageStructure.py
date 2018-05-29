import collections

gene_sets = {
    'arsenic' : {1,2,3,4,5,6,8,12},
    'cadmium' : {2,12,6,4},
    'copper' : {7,6,10,4,8},
    'mercury' : {3,2,4,5,1}
}

#print(gene_sets)

similarity_matrix={}
similarity_matrix = collections.defaultdict(lambda : 0)

for metal, genes in gene_sets.items():
    similarity_matrix[metal]
    similarity_matrix[metal]= collections.defaultdict(lambda : 0)
    print(similarity_matrix[metal])

for metal_matrix in similarity_matrix.items():
    print(metal)
    for metal_genes, genes in gene_sets.items():
        similarity_matrix[metal_matrix]=
    print(metal)

print(similarity_matrix['arsenic']['cadmium'])
print(similarity_matrix['arsenic']['lead'])
similarity_matrix['arsenic']['lead']=1,0

print(similarity_matrix['arsenic'])




#for metal1, genes1 in gene_sets.items():
    #print(metal1+" metal1")
   # print(similarity_matrix[metal1])
    #for metal2, genes2 in gene_sets.items():
        #for gene in genes2:
            #if gene in genes1:
                #print("found it")
                #similarity_matrix[metal1]=similarity_matrix[metal1]+1
        #print(metal1)
       # print(metal2)
#print(similarity_matrix)
