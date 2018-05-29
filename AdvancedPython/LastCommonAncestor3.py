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



def get_LCA(taxon1, taxon2):
    for ancestor in get_ancestors(taxon1):
        if ancestor in (get_ancestors(taxon2)):
           return ancestor



def get_ancestors(taxon):
    result = [taxon]
    while taxon != 'Primates' and taxon != None:
        parent = tax_dict.get(taxon)
        result.append(parent)
        taxon = parent
    return result

#def recurse_ancestors

print (get_LCA('Pan troglodytes','Galago alleni'))
#print(shared_ancestor)