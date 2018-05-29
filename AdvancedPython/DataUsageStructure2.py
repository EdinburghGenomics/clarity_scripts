gene_sets = {
    'arsenic' : {1,2,3,4,5,6,8,12},
    'cadmium' : {2,12,6,4},
    'copper' : {7,6,10,4,8},
    'mercury' : {3,2,4,5,1}
}
similarity_matrix={}
for_dict={}

for metal1, genes1 in gene_sets.items():
    #print(metal1+' intersections')
    for metal2, genes2 in gene_sets.items():
        if metal1 != metal2:
            #print('with '+metal2+' = '+ str(genes2.intersection(genes1)))
            for_dict[metal2]=((len(genes2.intersection(genes1)))/(len(genes2.union(genes1))))
    #print(for_dict)
    similarity_matrix[metal1]=for_dict

#print(similarity_matrix)
print('Similarity Score from arsenic and cadmium: '+str(similarity_matrix['arsenic']['cadmium']))

