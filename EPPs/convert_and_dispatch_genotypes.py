import csv
import sys
from os import remove
from os.path import join, dirname, abspath
from collections import defaultdict
from egcg_core.config import Configuration
from egcg_core.app_logging import AppLogger, logging_default as log_cfg

sys.path.append(dirname(dirname(abspath(__file__))))
from EPPs.common import EPP, argparser

etc_path = join(dirname(dirname(abspath(__file__))), 'etc')
snp_cfg = Configuration(join(etc_path, 'SNPs_definition.yml'))
default_fai = join(etc_path, 'genotype_32_SNPs_genome_600bp.fa.fai')
default_flank_length = 600

logger = log_cfg.get_logger(__name__)
SNPs_definitions = snp_cfg['GRCh37_32_SNPs']

# Accepted valid headers in the SNP CSV file
HEADERS_CALL = ['Call']
HEADERS_SAMPLE_ID = ['StudyID', 'Sample ID']
HEADERS_ASSAY_ID = ['SNPName', 'Assay Name']

vcf_header = ['#CHROM', 'POS', 'ID', 'REF', 'ALT', 'QUAL', 'FILTER', 'INFO', 'FORMAT']
start_vcf_header = ["##fileformat=VCFv4.1", '##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">']


class GenotypeConversion(AppLogger):
    def __init__(self, input_genotypes_content_files, input_accufill, mode, fai=default_fai, flank_length=default_flank_length):
        self.all_records = defaultdict(dict)
        self.sample_names = set()
        self.input_genotypes_content_files = input_genotypes_content_files
        self.fai = fai
        self.flank_length = flank_length
        self.input_accufill = input_accufill
        self._valid_array_barcodes = None
        self.info("Parsing genotypes in '%s' mode", mode)
        if mode == 'igmm':
            self.parse_genotype_csv()
        elif mode == 'quantStudio':
            if self.input_accufill:
                self.parse_quantstudio_flex_genotype()
            else:
                msg = 'Missing Accufill log file to confirm Array ids please provide with --accufill_log'
                self.critical(msg)
                raise ValueError(msg)
        else:
            raise ValueError('Unexpected genotype format: %s' % mode)

        self.info('Parsed %s samples', len(self.sample_names))

        reference_lengths = self._parse_genome_fai()
        self.vcf_header_contigs = self.vcf_header_from_ref_length(reference_lengths)
        self.snps_order = self.order_from_fai(self.all_records, reference_lengths)

    @staticmethod
    def get_genotype_from_call(ref_allele, alternate_allele, call):
        """Use the SNPs definition to convert the genotype call to a vcf compatible genotype"""
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
            msg = 'Call {call} does not match any of the alleles (ref:{ref_allele}, alt:{alternate_allele})'
            raise ValueError(msg.format(call=call, ref_allele=ref_allele, alternate_allele=alternate_allele))
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

    @staticmethod
    def _find_field(valid_fieldnames, observed_fieldnames):
        for f in observed_fieldnames:
            if f in valid_fieldnames:
                return f
        raise ValueError('Could not find any valid fields in ' + str(observed_fieldnames))

    def parse_genotype_csv(self):
        all_samples = set()
        all_records = defaultdict(dict)
        for input_genotypes_content_file in self.input_genotypes_content_files:
            with open(input_genotypes_content_file) as open_file:
                reader = csv.DictReader(open_file, delimiter='\t')
                fields = set(reader.fieldnames)

                header_sample_id = self._find_field(HEADERS_SAMPLE_ID, fields)
                header_assay_id = self._find_field(HEADERS_ASSAY_ID, fields)
                header_call = self._find_field(HEADERS_CALL, fields)

                for line in reader:
                    sample = line[header_sample_id]
                    if sample.lower() == 'blank':
                        # Entries with blank as sample name are entries with water and no DNA
                        continue
                    assay_id = line[header_assay_id]
                    self.add_genotype(sample, assay_id, line.get(header_call))

    def parse_quantstudio_flex_genotype(self):
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
            header_sample_id = self._find_field(['Sample Name'], sp_header)
            header_assay_id = self._find_field(['Assay ID'], sp_header)
            header_call = self._find_field(['Call'], sp_header)

            #Check the barcode is valid according to the accufill log file
            if not parameters['Barcode'] in self.valid_array_barcodes:
                msg = 'Array barcode %s is not in the list of valid barcodes (%s)' % (
                    parameters['Barcode'],
                    ', '.join(self.valid_array_barcodes)
                )
                self.critical(msg)
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
                    call_type, c = call.split()
                    e1, e2 = c.split('/')
                    a1 = snp_def.get(e1.split('_')[-1])
                    a2 = snp_def.get(e2.split('_')[-1])
                    call = a1 + a2
                self.add_genotype(sample, assay_id, call)

    def add_genotype(self, sample, assay_id, call):
        snp_def = SNPs_definitions.get(assay_id)
        genotype = self.get_genotype_from_call(snp_def['ref_base'], snp_def['alt_base'], call)
        if 'SNP' not in self.all_records[snp_def['snp_id']]:
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
        with open(self.fai) as open_file:
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
                all_arrays.add((line[header_array], line[header_holder], line[header_plate_barcode]))
        return all_arrays


    @property
    def valid_array_barcodes(self):
        if not self._valid_array_barcodes:
            array_info = self._parse_accufill_load_csv()
            self._valid_array_barcodes = list(set([a for a, h, p in array_info]))
        return self._valid_array_barcodes

class UploadVcfToSamples(EPP):
    def __init__(self, step_uri, username, password, log_file, mode, input_genotypes_files, accufill_log=None,
                 no_upload=False):
        super().__init__(step_uri, username, password, log_file)
        self.no_upload = no_upload
        self.geno_conv = GenotypeConversion(input_genotypes_files, accufill_log, mode, default_fai,
                                            default_flank_length)

    def _run(self):
        invalid_lims_samples = []
        valid_samples = []
        genotyping_sample_used = []
        artifacts = self.process.all_inputs()
        self.info('Matching against %s artifacts', len(artifacts))
        for artifact in artifacts:
            vcf_file = None
            # Assume only one sample per artifact
            lims_sample = artifact.samples[0]
            if lims_sample.name in self.geno_conv.sample_names:
                self.info('Matching %s' % lims_sample.name)
                vcf_file = self.geno_conv.generate_vcf(lims_sample.name)
                genotyping_sample_used.append(lims_sample.name)
            elif lims_sample.udf.get('User Sample Name') in self.geno_conv.sample_names:
                self.info('Matching %s against user sample name %s', lims_sample.name, lims_sample.udf.get('User Sample Name'))
                vcf_file = self.geno_conv.generate_vcf(lims_sample.udf.get('User Sample Name'), new_name=artifact.name)
                genotyping_sample_used.append(lims_sample.udf.get('User Sample Name'))
            else:
                self.info('No match found for %s', lims_sample.name)
                invalid_lims_samples.append(lims_sample)
            if vcf_file:
                valid_samples.append(lims_sample)
                if not self.no_upload:
                    file = self.lims.upload_new_file(lims_sample, vcf_file)
                    if file:
                        lims_sample.udf['Genotyping results file id'] = file.id
                        lims_sample.put()
                remove(vcf_file)

        unused_samples = set(self.geno_conv.sample_names).difference(set(genotyping_sample_used))

        self.info('Matched and uploaded %s artifacts against %s genotype results', len(set(valid_samples)), len(set(genotyping_sample_used)))
        self.info('%s artifacts did not match', len(set(invalid_lims_samples)))
        self.info('%s genotyping results were not used', len(unused_samples))

        # Message to print to stdout
        messages = []
        if invalid_lims_samples:
            messages.append('%s Samples are missing genotype' % len(invalid_lims_samples))
        if len(self.geno_conv.sample_names) - len(valid_samples) > 0:
            # TODO send a message to the EPP
            messages.append('%s genotypes have not been assigned' % (len(self.geno_conv.sample_names) - len(valid_samples)))
        print(', '.join(messages))


def main():
    args = _parse_args()
    action = UploadVcfToSamples(args.step_uri, args.username, args.password, args.log_file, args.format,
                                args.input_genotypes, args.accufill_log, args.no_upload)
    action.run()


def _parse_args():
    p = argparser()
    p.add_argument('--format', dest='format', type=str, choices=['igmm', 'quantStudio'],
                   help='The format of the genotype file')
    p.add_argument('--input_genotypes', dest='input_genotypes', type=str, nargs='+',
                   help='The file that contains the genotype for all the samples')
    p.add_argument('--accufill_log', dest='accufill_log', type=str, required=False,
                   help='The file that contains the location and name of each of the array')
    p.add_argument('--no_upload', dest='no_upload', action='store_true', help='Prevent any upload to the LIMS')
    return p.parse_args()


if __name__ == '__main__':
    main()
