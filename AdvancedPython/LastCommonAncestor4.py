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


def get_lca_list(taxa):
    #taxon1 = taxa.pop()
    #print(taxon1)
    taxon2 = taxa[2]
    print(taxon2)
    while len(taxa) > 0:
        taxon2=taxa[0]
        print(taxon2)
        taxon2 = taxa.pop()
        print(taxon2)

print(get_lca_list(['Pan troglodytes','Tarsius tarsier', 'Pongo abelii']))