import argparse
import logging
import os
import re
import sys
from sys import version_info

if version_info.major == 2:
    import urlparse
else:
    from urllib import parse as urlparse

from genologics.entities import Process, Artifact
from genologics.lims import Lims
from collections import defaultdict
import csv

__author__ = 'tcezard'

logger = logging.getLogger(__name__)

SNPs_definitions = {
    'C___2728408_10': {'V': 'C', 'M': 'T', 'snp_id': 'rs3010325', 'chr': '1', 'pos': '59569829', 'ref_base': 'C',
                       'alt_base': 'T', 'design_strand': 'Reverse'},
    'C___1563023_10': {'V': 'C', 'M': 'T', 'snp_id': 'rs2136241', 'chr': '1', 'pos': '163289571', 'ref_base': 'C',
                       'alt_base': 'T', 'design_strand': 'Reverse'},
    'C__15935210_10': {'V': 'C', 'M': 'T', 'snp_id': 'rs2259397', 'chr': '1', 'pos': '208068579', 'ref_base': 'T',
                       'alt_base': 'C', 'design_strand': 'Reverse'},
    'C__33211212_10': {'V': 'A', 'M': 'G', 'snp_id': 'rs7564899', 'chr': '2', 'pos': '11200347', 'ref_base': 'G',
                       'alt_base': 'A', 'design_strand': 'Forward'},
    'C___3227711_10': {'V': 'C', 'M': 'T', 'snp_id': 'rs4971536', 'chr': '2', 'pos': '21084332', 'ref_base': 'C',
                       'alt_base': 'T', 'design_strand': 'Reverse'},
    'C__30044763_10': {'V': 'A', 'M': 'G', 'snp_id': 'rs10194978', 'chr': '2', 'pos': '50525067', 'ref_base': 'G',
                       'alt_base': 'A', 'design_strand': 'Forward'},
    'C__11821218_10': {'V': 'A', 'M': 'G', 'snp_id': 'rs4855056', 'chr': '3', 'pos': '181638250', 'ref_base': 'A',
                       'alt_base': 'G', 'design_strand': 'Forward'},
    'C___1670459_10': {'V': 'C', 'M': 'T', 'snp_id': 'rs6554653', 'chr': '5', 'pos': '11870138', 'ref_base': 'C',
                       'alt_base': 'T', 'design_strand': 'Reverse'},
    'C___1007630_10': {'V': 'A', 'M': 'G', 'snp_id': 'rs441460', 'chr': '6', 'pos': '2554828', 'ref_base': 'G',
                       'alt_base': 'A', 'design_strand': 'Reverse'},
    'C__29619553_10': {'V': 'C', 'M': 'T', 'snp_id': 'rs9396715', 'chr': '6', 'pos': '9914294', 'ref_base': 'T',
                       'alt_base': 'C', 'design_strand': 'Reverse'},
    'C__26546714_10': {'V': 'G', 'M': 'T', 'snp_id': 'rs7773994', 'chr': '6', 'pos': '37572144', 'ref_base': 'T',
                       'alt_base': 'G', 'design_strand': 'Forward'},
    'C___7421900_10': {'V': 'C', 'M': 'T', 'snp_id': 'rs1415762', 'chr': '6', 'pos': '125039942', 'ref_base': 'C',
                       'alt_base': 'T', 'design_strand': 'Forward'},
    'C__27402849_10': {'V': 'C', 'M': 'T', 'snp_id': 'rs6927758', 'chr': '6', 'pos': '163719115', 'ref_base': 'C',
                       'alt_base': 'T', 'design_strand': 'Reverse'},
    'C___2953330_10': {'V': 'A', 'M': 'G', 'snp_id': 'rs7796391', 'chr': '7', 'pos': '126113335', 'ref_base': 'A',
                       'alt_base': 'G', 'design_strand': 'Reverse'},
    'C__16205730_10': {'V': 'A', 'M': 'G', 'snp_id': 'rs2336695', 'chr': '8', 'pos': '1033625', 'ref_base': 'A',
                       'alt_base': 'G', 'design_strand': 'Forward'},
    'C___8850710_10': {'V': 'C', 'M': 'T', 'snp_id': 'rs1157213', 'chr': '8', 'pos': '10421546', 'ref_base': 'T',
                       'alt_base': 'C', 'design_strand': 'Forward'},
    'C___1801627_20': {'V': 'A', 'M': 'C', 'snp_id': 'rs10869955', 'chr': '9', 'pos': '80293657', 'ref_base': 'C',
                       'alt_base': 'A', 'design_strand': 'Reverse'},
    'C___7431888_10': {'V': 'G', 'M': 'T', 'snp_id': 'rs1533486', 'chr': '10', 'pos': '1511786', 'ref_base': 'T',
                       'alt_base': 'G', 'design_strand': 'Forward'},
    'C___1250735_20': {'V': 'A', 'M': 'G', 'snp_id': 'rs4751955', 'chr': '10', 'pos': '117923225', 'ref_base': 'A',
                       'alt_base': 'G', 'design_strand': 'Forward'},
    'C___1902433_10': {'V': 'C', 'M': 'T', 'snp_id': 'rs10771010', 'chr': '12', 'pos': '23769449', 'ref_base': 'T',
                       'alt_base': 'C', 'design_strand': 'Forward'},
    'C__31386842_10': {'V': 'C', 'M': 'T', 'snp_id': 'rs12318959', 'chr': '12', 'pos': '28781965', 'ref_base': 'C',
                       'alt_base': 'T', 'design_strand': 'Reverse'},
    'C__26524789_10': {'V': 'C', 'M': 'T', 'snp_id': 'rs3742257', 'chr': '13', 'pos': '43173198', 'ref_base': 'T',
                       'alt_base': 'C', 'design_strand': 'Forward'},
    'C___8924366_10': {'V': 'C', 'M': 'T', 'snp_id': 'rs1377935', 'chr': '14', 'pos': '25843774', 'ref_base': 'T',
                       'alt_base': 'C', 'design_strand': 'Reverse'},
    'C_____43852_10': {'V': 'A', 'M': 'C', 'snp_id': 'rs946065', 'chr': '14', 'pos': '55932919', 'ref_base': 'C',
                       'alt_base': 'A', 'design_strand': 'Forward'},
    'C__11522992_10': {'V': 'G', 'M': 'T', 'snp_id': 'rs6598531', 'chr': '15', 'pos': '99130113', 'ref_base': 'T',
                       'alt_base': 'G', 'design_strand': 'Forward'},
    'C__10076371_10': {'V': 'C', 'M': 'T', 'snp_id': 'rs4783229', 'chr': '16', 'pos': '82622140', 'ref_base': 'T',
                       'alt_base': 'C', 'design_strand': 'Reverse'},
    'C___7457509_10': {'V': 'A', 'M': 'G', 'snp_id': 'rs1567612', 'chr': '18', 'pos': '35839365', 'ref_base': 'G',
                       'alt_base': 'A', 'design_strand': 'Forward'},
    'C___1122315_10': {'V': 'A', 'M': 'G', 'snp_id': 'rs11660213', 'chr': '18', 'pos': '42481985', 'ref_base': 'A',
                       'alt_base': 'G', 'design_strand': 'Reverse'},
    'C__11710129_10': {'V': 'A', 'M': 'G', 'snp_id': 'rs11083515', 'chr': '19', 'pos': '39697974', 'ref_base': 'A',
                       'alt_base': 'G', 'design_strand': 'Forward'},
    'C___1027548_20': {'V': 'T', 'M': 'C', 'snp_id': 'rs768983', 'chr': 'Y', 'pos': '6818291', 'ref_base': 'C',
                       'alt_base': 'T', 'design_strand': 'Reverse'},
    'C___8938211_20': {'V': 'T', 'M': 'C', 'snp_id': 'rs3913290', 'chr': 'Y', 'pos': '8602518', 'ref_base': 'C',
                       'alt_base': 'T', 'design_strand': 'Forward'},
    'C___1083232_10': {'V': 'T', 'M': 'C', 'snp_id': 'rs2032598', 'chr': 'Y', 'pos': '14850341', 'ref_base': 'T',
                       'alt_base': 'C', 'design_strand': 'Reverse'}
}

HEADERS_CALL = ["Call"]
# Actual Header in the file
HEADERS_SAMPLE_ID = ["StudyID", 'Sample ID']
HEADERS_ASSAY_ID = ["SNPName", "Assay Name"]

vcf_header = ['#CHROM', 'POS', 'ID', 'REF', 'ALT', 'QUAL', 'FILTER', 'INFO', 'FORMAT']
start_vcf_header = ["##fileformat=VCFv4.1", '##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">']


class Genotype_conversion(object):
    def __init__(self, input_genotypes_content_files, input_accufill, genome_fai, geno_format, flank_length=0):
        self.all_records = defaultdict(dict)
        self.sample_names = set()
        self.input_genotypes_content_files = input_genotypes_content_files
        self.genome_fai = genome_fai
        self.flank_length = flank_length
        self.input_accufill = input_accufill
        self._valid_array_barcodes = None
        if geno_format == 'igmm':
            self.parse_genotype_csv()
        elif geno_format == 'quantStudio':
            if self.input_accufill:
                self.parse_QuantStudio_flex_genotype()
            else:
                msg = 'Missing Accufill log file to confirm Array ids please provide with --accufill_log'
                logging.error(msg)
                raise ValueError(msg)
        else:
            raise ValueError('Unexpected format %s' % geno_format)
        reference_lengths = self._parse_genome_fai()
        self.vcf_header_contigs = self.vcf_header_from_ref_length(reference_lengths)
        self.snps_order = self.order_from_fai(self.all_records, reference_lengths)

    @staticmethod
    def get_genotype_from_call(ref_allele, alternate_allele, call):
        """Uses the SNPs definition to convert the genotype call to a vcf compatible genotype"""
        genotype = './.'
        if call.lower() == 'undefined' or call.lower() == 'undetermined':
            return genotype
        if call == 'Both':
            call = ref_allele + alternate_allele
        callset = set(call)
        if ref_allele in callset and len(callset) == 1:
            genotype = '0/0'
        elif ref_allele in callset and alternate_allele in callset:
            genotype = '0/1'
            callset.remove(ref_allele)
        elif alternate_allele in callset and len(callset) == 1:
            genotype = '1/1'
        else:
            raise ValueError("Call {} does not match any of the alleles (ref:{}, alt:{})".format(call, ref_allele,
                                                                                                 alternate_allele))
        return genotype

    @staticmethod
    def vcf_header_from_ref_length(reference_lengths):
        """Generate a vcf header from ref names and length from the fai file"""
        header_entries = []
        for ref_name, length in reference_lengths:
            header_entries.append('##contig=<ID=%s,length=%s>' % (ref_name, length))
        return header_entries

    @staticmethod
    def order_from_fai(all_records, reference_lengths):
        ordered_snp_ids = []
        for ref_name, length in reference_lengths:
            # Extract all the record on a particular reference
            snps = [rec.get('SNP') for rec in all_records.values() if rec['SNP'][0] == ref_name]
            # Sort the SNPs by position within a reference
            snps.sort(key=lambda snp: int(snp[1]))
            # get the snp id as the key
            ordered_snp_ids.extend([rec[2] for rec in snps])
        return ordered_snp_ids

    def parse_genotype_csv(self):
        all_samples = set()
        all_records = defaultdict(dict)
        for input_genotypes_content_file in self.input_genotypes_content_files:
            with open(input_genotypes_content_file) as open_file:
                reader = csv.DictReader(open_file, delimiter='\t')
                fields = set(reader.fieldnames)
                for h in fields:
                    if h in HEADERS_SAMPLE_ID:
                        header_sample_id = h
                    elif h in HEADERS_ASSAY_ID:
                        header_assay_id = h
                    elif h in HEADERS_CALL:
                        header_call = h
                for line in reader:
                    sample = line[header_sample_id]
                    if sample.lower() == 'blank':
                        # Entries with blank as sample name are entries with water and no DNA
                        continue
                    assay_id = line[header_assay_id]
                    self.add_genotype(sample, assay_id, line.get(header_call))

        return all_records, list(all_samples)

    def parse_QuantStudio_flex_genotype(self):
        result_lines = []
        in_results = False
        parameters = {}
        for input_genotypes_content_file in self.input_genotypes_content_files:
            with open(input_genotypes_content_file) as open_file:
                for line in open_file:
                    if not line.strip():
                        continue
                    elif line.startswith('*'):
                        k, v = line.strip().strip('*').split('=')
                        parameters[k.strip()] = v.strip()

                    elif in_results:
                        result_lines.append(line.strip())
                    elif line.startswith('[Results]'):
                        in_results = True
            sp_header = result_lines[0].split('\t')
            for h in sp_header:
                if h in ['Sample Name']:
                    header_sample_id = h
                elif h in ['Assay ID']:
                    header_assay_id = h
                elif h in ['Call']:
                    header_call = h

            #Check the barcode is valid according to the accufill log file
            if not parameters['Barcode'] in self.valid_array_barcodes:
                msg = 'Array barcode %s is not in the list of valid barcodes (%s)' % (
                    parameters['Barcode'],
                    ', '.join(self.valid_array_barcodes)
                )
                logger.critical(msg)
                raise ValueError(msg)
            else:
                logger.info('Validate array barcode %s'%(parameters['Barcode']))


            for line in result_lines[1:]:
                sp_line = line.split('\t')
                sample = sp_line[sp_header.index(header_sample_id)]
                if sample.lower() == 'blank':
                    # Entries with blank as sample name are entries with water and no DNA
                    continue
                assay_id = sp_line[sp_header.index(header_assay_id)]
                snp_def = SNPs_definitions.get(assay_id)
                call = sp_line[sp_header.index(header_call)]

                if not call == 'Undetermined':
                    type, c = call.split()
                    e1, e2 = c.split('/')
                    a1 = snp_def.get(e1.split('_')[-1])
                    a2 = snp_def.get(e2.split('_')[-1])
                    call = a1 + a2
                self.add_genotype(sample, assay_id, call)

    def add_genotype(self, sample, assay_id, call):
        snp_def = SNPs_definitions.get(assay_id)
        genotype = self.get_genotype_from_call(snp_def['ref_base'], snp_def['alt_base'], call)
        if not 'SNP' in self.all_records[snp_def['snp_id']]:
            if self.flank_length:
                snp = [assay_id, str(self.flank_length + 1), snp_def['snp_id'],
                       snp_def['ref_base'], snp_def['alt_base'], ".", ".", ".", "GT"]
            else:
                snp = [snp_def['chr'], snp_def['pos'], snp_def['snp_id'],
                       snp_def['ref_base'], snp_def['alt_base'], ".", ".", ".", "GT"]
            self.all_records[snp_def['snp_id']]['SNP'] = snp
        if sample in self.all_records[snp_def['snp_id']]:
            raise Exception('Sample {} found more than once for SNPs {}'.format(sample, snp_def['snp_id']))
        self.all_records[snp_def['snp_id']][sample] = genotype
        self.sample_names.add(sample)

    def _parse_genome_fai(self):
        reference_lengths = []
        with open(self.genome_fai) as open_file:
            reader = csv.reader(open_file, delimiter='\t')
            for row in reader:
                reference_lengths.append((row[0], row[1]))
        return reference_lengths

    def generate_vcf(self, sample, new_name=None):
        if not new_name:
            new_name = sample
        vcf_file = new_name + '.vcf'
        lines = []
        lines.extend(start_vcf_header)
        lines.extend(self.vcf_header_contigs)
        lines.append('\t'.join(list(vcf_header) + [new_name]))
        for snps_id in self.snps_order:
            out = list(self.all_records[snps_id].get('SNP'))
            out.append(self.all_records[snps_id].get(sample))
            lines.append('\t'.join(out))
        with open(vcf_file, 'w') as open_file:
            open_file.write('\n'.join(lines))
        return vcf_file


    def _parse_accufill_load_csv(self):
        all_arrays = set()
        with open(self.input_accufill) as open_file:
            reader = csv.DictReader(open_file, delimiter='\t')
            header_holder = 'Plate Holder Position'
            header_plate_barcode = 'Sample Plate Barcode'
            header_array = 'OpenArray Plate Barcode'
            for line in reader:
                all_arrays.add( (line[header_array], line[header_holder], line[header_plate_barcode]) )
        return all_arrays

    @property
    def valid_array_barcodes(self):
        if not self._valid_array_barcodes:
            array_info = self._parse_accufill_load_csv()
            self._valid_array_barcodes = list(set([a for a, h, p in array_info]))
        return self._valid_array_barcodes


def get_lims_sample(sample_name, lims):
    samples = lims.get_samples(name=sample_name)
    if len(samples) == 0:
        sample_name_sub = re.sub("_(\d{2})$", ":\g<1>", sample_name)
        samples = lims.get_samples(name=sample_name_sub)
    if len(samples) == 0:
        sample_name_sub = re.sub("__(\w)_(\d{2})", " _\g<1>:\g<2>", sample_name)
        samples = lims.get_samples(name=sample_name_sub)

    if len(samples) != 1:
        logger.warning('%s Sample(s) found for name %s' % (len(samples), sample_name))
        return None

    return samples[0]


def upload_vcf_to_samples(geno_conv, lims, p, no_upload=False):
    invalid_lims_samples = []
    valid_samples = []
    genotyping_sample_used = []
    artifacts = p.all_inputs()
    logger.info('Match against %s artifacts' % len(artifacts))
    for artifact in artifacts:
        vcf_file = None
        # Assume only one sample per artifact
        lims_sample = artifact.samples[0]
        if lims_sample.name in geno_conv.sample_names:
            logger.info('Matching %s' % lims_sample.name)
            vcf_file = geno_conv.generate_vcf(lims_sample.name)
            genotyping_sample_used.append(lims_sample.name)
        elif lims_sample.udf.get('User Sample Name') in geno_conv.sample_names:
            logger.info(
                'Matching %s against user sample name %s' % (lims_sample.name, lims_sample.udf.get('User Sample Name')))
            vcf_file = geno_conv.generate_vcf(lims_sample.udf.get('User Sample Name'), new_name=artifact.name)
            genotyping_sample_used.append(lims_sample.udf.get('User Sample Name'))
        else:
            logger.info('No match found for %s' % (lims_sample.name))
            invalid_lims_samples.append(lims_sample)
        if vcf_file:
            valid_samples.append(lims_sample)
            if not no_upload:
                file = lims.upload_new_file(lims_sample, vcf_file)
                if file:
                    lims_sample.udf['Genotyping results file id'] = file.id
                    lims_sample.put()
            os.remove(vcf_file)
    logger.info('Match and uploaded %s artifacts against %s genotype results' % (
    len(set(valid_samples)), len(set(genotyping_sample_used))))
    logger.info('%s artifacts did not match' % (len(set(invalid_lims_samples))))
    logger.info('%s genotyping results were not used' % (
    len(set(geno_conv.sample_names).difference(set(genotyping_sample_used)))))

    # Message to print to stdout
    messages = []
    if invalid_lims_samples:
        messages.append("%s Samples are missing genotype" % len(invalid_lims_samples))
    if len(geno_conv.sample_names) - len(valid_samples) > 0:
        # TODO send a message to the EPP
        messages.append("%s genotypes have not been assigned" % (len(geno_conv.sample_names) - len(valid_samples)))
    print(', '.join(messages))



def main():
    args = _parse_args()
    genome_fai = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'etc', 'genotype_32_SNPs_genome_600bp.fa.fai')
    flank_length = 600
    r1 = urlparse.urlsplit(args.step_uri)
    server_http = '%s://%s' % (r1.scheme, r1.netloc)
    # Assume the step_uri contains the step id at the end
    step_id = r1.path.split('/')[-1]
    lims = Lims(server_http, args.username, args.password)
    # setup logging
    level = logging.INFO
    logger.setLevel(level)
    formatter = logging.Formatter(
        fmt='[%(asctime)s] [%(levelname)s] %(message)s',
        datefmt='%Y-%b-%d %H:%M:%S'
    )
    if args.log_file:
        handler = logging.FileHandler(args.log_file)
    else:
        handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    handler.setLevel(level)
    logger.addHandler(handler)

    p = Process(lims, id=step_id)

    try:
        logger.info('Parse the genotyping files in format %s' % args.format)
        geno_conv = Genotype_conversion(
            args.input_genotypes,
            args.accufill_log,
            genome_fai,
            args.format,
            flank_length
        )
        logger.info('%s samples parsed' % (len(geno_conv.sample_names)))
        upload_vcf_to_samples(geno_conv, lims, p, no_upload=args.no_upload)

    except Exception as e:
        logger.critical('Encountered a %s exception: %s', e.__class__.__name__, str(e))
        import traceback
        stacktrace = traceback.format_exc()
        logger.info('Stack trace below:\n' + stacktrace)
        raise e


def _parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--username', dest="username", type=str, help='The username of the person logged in')
    p.add_argument('--password', dest="password", type=str, help='The password used by the person logged in')
    p.add_argument('--step_uri', dest='step_uri', type=str, help='The uri of the step this EPP is attached to')
    p.add_argument('--format', dest='format', type=str, choices=['igmm', 'quantStudio'],
                   help='The format of the genotype file')
    p.add_argument('--input_genotypes', dest='input_genotypes', type=str, nargs='+',
                   help='The files that contain the genotype for all the samples')
    p.add_argument('--accufill_log', dest='accufill_log', type=str, required=False,
                   help='The file that contains the location and name of each of the array')
    p.add_argument('--log_file', dest='log_file', type=str, help='log file uploaded back to the LIMS')
    p.add_argument('--no_upload', dest='no_upload', action='store_true', help='Prevent any upload to the LIMS')
    return p.parse_args()


if __name__ == "__main__":
    main()
