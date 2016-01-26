import argparse

import genologics

from collections import defaultdict
import csv

__author__ = 'tcezard'

SNPs_definition = {"C___2728408_10": ["rs3010325",  "1",  "59569829",  "C", "T", "Reverse"],
                   "C___1563023_10": ["rs2136241",  "1",  "163289571", "C", "T", "Reverse"],
                   "C__15935210_10": ["rs2259397",  "1",  "208068579", "T", "C", "Reverse"],
                   "C__33211212_10": ["rs7564899",  "2",  "11200347",  "G", "A", "Forward"],
                   "C___3227711_10": ["rs4971536",  "2",  "21084332",  "C", "T", "Reverse"],
                   "C__30044763_10": ["rs10194978", "2",  "50525067",  "G", "A", "Forward"],
                   "C__11821218_10": ["rs4855056",  "3",  "181638250", "A", "G", "Forward"],
                   "C___1670459_10": ["rs6554653",  "5",  "11870138",  "C", "T", "Reverse"],
                   "C__29619553_10": ["rs9396715",  "6",  "9914294",   "T", "C", "Reverse"],
                   "C___1007630_10": ["rs441460",   "6",  "25548288",  "G", "A", "Reverse"],
                   "C__26546714_10": ["rs7773994",  "6",  "37572144",  "T", "G", "Forward"],
                   "C___7421900_10": ["rs1415762",  "6",  "125039942", "C", "T", "Forward"],
                   "C__27402849_10": ["rs6927758",  "6",  "163719115", "C", "T", "Reverse"],
                   "C___2953330_10": ["rs7796391",  "7",  "126113335", "A", "G", "Reverse"],
                   "C__16205730_10": ["rs2336695",  "8",  "1033625",   "A", "G", "Forward"],
                   "C___8850710_10": ["rs1157213",  "8",  "104215466", "T", "C", "Forward"],
                   "C___1801627_20": ["rs10869955", "9",  "80293657",  "C", "A", "Reverse"],
                   "C___7431888_10": ["rs1533486",  "10", "1511786",   "T", "G", "Forward"],
                   "C___1250735_20": ["rs4751955",  "10", "117923225", "A", "G", "Forward"],
                   "C___1902433_10": ["rs10771010", "12", "23769449",  "T", "C", "Forward"],
                   "C__31386842_10": ["rs12318959", "12", "28781965",  "C", "T", "Reverse"],
                   "C__26524789_10": ["rs3742257",  "13", "43173198",  "T", "C", "Forward"],
                   "C___8924366_10": ["rs1377935",  "14", "25843774",  "T", "C", "Reverse"],
                   "C_____43852_10": ["rs946065",   "14", "55932919",  "C", "A", "Forward"],
                   "C__11522992_10": ["rs6598531",  "15", "99130113",  "T", "G", "Forward"],
                   "C__10076371_10": ["rs4783229",  "16", "82622140",  "T", "C", "Reverse"],
                   "C___7457509_10": ["rs1567612",  "18", "35839365",  "G", "A", "Forward"],
                   "C___1122315_10": ["rs11660213", "18", "42481985",  "A", "G", "Reverse"],
                   "C__11710129_10": ["rs11083515", "19", "39697974",  "A", "G", "Forward"],
                   "C___1027548_20": ["rs768983",   "Y",  "6818291",   "C", "T", "Reverse"],
                   "C___8938211_20": ["rs3913290",  "Y",  "8602518",   "C", "T", "Forward"],
                   "C___1083232_10": ["rs2032598",  "Y",  "14850341",  "T", "C", "Reverse"]}

HEADERS_CALL="Call"
#Actual Header in the file
HEADERS_SAMPLE_ID = ["StudyID", 'Sample ID']
HEADERS_ASSAY_ID=["SNPName", "Assay Name"]

vcf_header=['#CHROM','POS','ID','REF','ALT','QUAL','FILTER','INFO','FORMAT']


def get_genotype_from_call(ref_allele, alternate_allele, call):
    """Uses the SNPs definition to convert the genotype call to a vcf compatible genotype"""
    genotype = './.'
    if call.lower() == 'undefined' or call.lower() == 'undetermined':
        return genotype
    if call == 'Both':
        call=ref_allele + alternate_allele
    callset = set(call)
    if ref_allele in callset and len(callset) == 1:
        genotype='0/0'
    elif ref_allele in callset and alternate_allele in callset:
        genotype='0/1'
        callset.remove(ref_allele)
    elif alternate_allele in callset and len(callset) == 1:
        genotype='1/1'
    else:
        raise ValueError("Call {} does not match any of the alleles (ref:{}, alt:{})".format(call, ref_allele,
                                                                                             alternate_allele))
    return genotype


def vcf_header_from_fai_file(genome_fai):
    """Generate a vcf header from an fai file"""
    header_entries = []
    with open(genome_fai) as open_file:
        reader = csv.reader(open_file, delimiter='\t')
        for row in reader:
            header_entries.append('##contig=<ID=%s,length=%s>'%(row[0], row[1]))
    return header_entries

def order_from_fai(all_records, genome_fai):
    ordered_records = []
    with open(genome_fai) as open_file:
        reader = csv.reader(open_file, delimiter='\t')
        for row in reader:
            snps = all_records.get(row[0], [])
            #Sort the SNPs by position within a ref
            snps.sort(key=lambda snp: int(snp[1]))
            #convert the array to str
            ordered_records.extend(['\t'.join(s) for s in snps])
    return ordered_records

def convert_genotype_csv(csv_file, genome_fai, flank_length=0):
    all_samples = set()
    with open(csv_file) as open_file:
        reader = csv.DictReader(open_file, delimiter='\t')
        all_records = defaultdict(dict)
        fields = set(reader.fieldnames)
        for h in  HEADERS_SAMPLE_ID:
            if h in fields:
                header_sample_id = h
        for h in  HEADERS_ASSAY_ID:
            if h in fields:
                header_assay_id = h
        for line in reader:
            sample = line[header_sample_id]
            if sample.lower() =='blank':
                #Entries with blank as sample name are entries with water and no DNA
                continue
            assay_id = line[header_assay_id]
            SNPs_id, reference_name, reference_position, ref_allele, alt_allele, design_strand = SNPs_definition.get(assay_id)
            #alt_allele is the alternate allele from the dbsnp definition
            #It will be replaced by the alt allele from the call if it exists
            genotype = get_genotype_from_call(ref_allele, alt_allele, line.get(HEADERS_CALL))
            if not 'SNPs' in all_records[SNPs_id]:
                if flank_length:
                    SNP=[assay_id, str(flank_length+1), SNPs_id, ref_allele, alt_allele, ".", ".", ".", "GT"]
                else:
                    SNP=[reference_name, reference_position, SNPs_id, ref_allele, alt_allele, ".", ".", ".", "GT"]
                all_records[SNPs_id]['SNP']=SNP
            if sample in all_records[SNPs_id]:
                raise Exception('Sample {} found more than once for SNPs {}'.format(sample, SNPs_id))
            all_records[SNPs_id][sample]=genotype
            all_samples.add(sample)

    all_samples = sorted(all_samples)
    SNPs_list = defaultdict(list)
    for SNPs_id in  all_records:
        record = all_records.get(SNPs_id)
        out = record.get('SNP')
        out.extend([record.get(sample) for sample in all_samples])
        SNPs_list[out[0]].append(out)

    all_lines = ["##fileformat=VCFv4.1",
                 '##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">']
    all_lines.extend(vcf_header_from_fai_file(genome_fai))
    vcf_header.extend(all_samples)
    all_lines.append('\t'.join(vcf_header))
    all_lines.extend(order_from_fai(SNPs_list, genome_fai))
    return '\n'.join(all_lines)


def main():
    args = _parse_args()


def _parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--username', dest="username", type=str, help='The username of the person logged in')
    p.add_argument('--password', dest="password", type=str, help='The password used by the person logged in')
    p.add_argument('--process_id', dest='process_id', type=str, help='The id of the process this EPP is attached to')
    p.add_argument('--input_genotypes', dest='input_genotypes', type=str, help='The file that contains the genotype for all the samples')

    return p.parse_args()

if __name__ == "__main__":
    main()