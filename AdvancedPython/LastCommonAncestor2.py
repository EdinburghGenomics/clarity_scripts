tax_dict = {
'Pan troglodytes' : 'Hominoidea',       'Pongo abelii' : 'Hominoidea',
'Hominoidea' :  'Simiiformes',          'Simiiformes' : 'Haplorrhini',
'Tarsius tarsier' : 'Tarsiiformes',     'Haplorrhini' : 'Primates',
'Tarsiiformes' : 'Haplorrhini',         'Loris tardigradus' : 'Lorisidae',
'Lorisidae' : 'Strepsirrhini',          'Strepsirrhini' : 'Primates',
'Allocebus trichotis' : 'Lemuriformes', 'Lemuriformes' : 'Strepsirrhini',
'Galago alleni' : 'Lorisiformes',       'Lorisiformes' : 'Strepsirrhini',
'Galago moholi' : 'Lorisiformes'
}



def get_LCA(species):
    global shared_ancestor

    for ancestor in (get_ancestors(species[0])):
        if ancestor in (get_ancestors(species[1])):
            shared_ancestor=ancestor
            print(shared_ancestor)


    #print(species)
    #for specie in species:
            #for specie2 in species:
                #for ancestor in (get_ancestors(specie)):
                    #if ancestor in (get_ancestors(specie2)) and specie !=specie2:
                        #shared_ancestor=ancestor



def get_ancestors(taxon):
    if taxon == 'Primates':
        return []
    else:
        parent = tax_dict.get(taxon)
        parent_ancestors = get_ancestors(parent)
        #print(parent)
        return [parent] + parent_ancestors



get_LCA(['Pan troglodytes','Galago alleni'])
#print(shared_ancestor)