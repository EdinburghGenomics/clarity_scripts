#!/usr/bin/env python
import sys
import csv
from collections import defaultdict
from os import remove
from os.path import join, dirname, abspath
from egcg_core.app_logging import AppLogger
from egcg_core.config import Configuration
import EPPs
from EPPs.common import StepEPP, step_argparser

etc_path = join(abspath(dirname(EPPs.__file__)), 'etc')
snp_cfg = Configuration(join(etc_path, 'SNPs_definition.yml'))
default_fai = join(etc_path, 'genotype_32_SNPs_genome_600bp.fa.fai')
default_flank_length = 600

SNPs_definitions = snp_cfg['GRCh37_32_SNPs']

# Accepted valid headers in the SNP CSV file
HEADERS_CALL = ['Call']
HEADERS_SAMPLE_ID = ['StudyID', 'Sample ID']
HEADERS_ASSAY_ID = ['SNPName', 'Assay Name']

vcf_header = ['#CHROM', 'POS', 'ID', 'REF', 'ALT', 'QUAL', 'FILTER', 'INFO', 'FORMAT']
start_vcf_header = ["##fileformat=VCFv4.1", '##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">']

genotype_udf_file_id = 'Genotyping results file id'
output_genotype_udf_number_call = 'Number of Calls (This Run)'
submitted_genotype_udf_number_call = 'Number of Calls (Best Run)'
submitted_nb_genotype_tries = 'QuantStudio Data Import Completed #'


class GenotypeConversion(AppLogger):
    def __init__(self, input_genotypes_contents, fai=default_fai, flank_length=default_flank_length):
        self.all_records = defaultdict(dict)
        self.sample_names = set()
        self.input_genotypes_contents = input_genotypes_contents
        self.fai = fai
        self.flank_length = flank_length
        self._valid_array_barcodes = None

        self.parse_quantstudio_flex_genotype()
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

    def parse_quantstudio_flex_genotype(self):
        for input_genotypes_content in self.input_genotypes_contents:
            result_lines = []
            in_results = False
            parameters = {}
            for line in input_genotypes_content:
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

            for line in result_lines[1:]:
                sp_line = line.split('\t')
                sample = sp_line[sp_header.index(header_sample_id)]
                if not sample or sample.lower() == 'blank':
                    # Entries with blank as sample name are entries with water and no DNA
                    continue
                assay_id = sp_line[sp_header.index(header_assay_id)]
                snp_def = SNPs_definitions.get(assay_id)
                if not snp_def:
                    # Remove control wells
                    continue
                assay_id = sp_line[sp_header.index(header_assay_id)]
                snp_def = SNPs_definitions.get(assay_id)
                call = sp_line[sp_header.index(header_call)]

                if not call == 'Undetermined':
                    sp_call = call.split()

                    e1, e2 = ' '.join(sp_call[1:]).split('/')
                    if e1 == 'Allele 1':
                        a1 = snp_def.get('V')
                    elif e1 == 'Allele 2':
                        a1 = snp_def.get('M')
                    else:
                        a1 = snp_def.get(e1.split('_')[-1])
                    if e2 == 'Allele 1':
                        a2 = snp_def.get('V')
                    elif e2 == 'Allele 2':
                        a2 = snp_def.get('M')
                    else:
                        a2 = snp_def.get(e2.split('_')[-1])
                    call = a1 + a2
                self.add_genotype(sample, assay_id, call, parameters['Barcode'])

    def add_genotype(self, sample, assay_id, call, array_barcode=None):
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
            msg = 'Sample {} found more than once for SNPs {} while parsing {}'.format(sample, snp_def['snp_id'],
                                                                                       array_barcode)
            self.critical(msg)
            raise Exception(msg)
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
            genotype = self.all_records[snps_id].get(sample)
            if genotype:
                out = list(self.all_records[snps_id].get('SNP'))
                out.append(self.all_records[snps_id].get(sample))
                lines.append('\t'.join(out))
            else:
                msg = 'SNP %s was not found for sample %s' % (snps_id, sample)
                self.critical(msg)
                raise ValueError(msg)
        with open(vcf_file, 'w') as open_file:
            open_file.write('\n'.join(lines))
        return vcf_file

    def nb_calls(self, sample):
        return sum([1 for snps_id in self.snps_order if self.all_records[snps_id].get(sample) != './.'])


class UploadVcfToSamples(StepEPP):
    def __init__(self, step_uri, username, password, log_file, input_genotypes_files):
        super().__init__(step_uri, username, password, log_file)
        input_genotypes_contents = []
        for s in input_genotypes_files:
            f = self.open_or_download_file(s)
            if f:
                input_genotypes_contents.append(f)
        self.geno_conv = GenotypeConversion(input_genotypes_contents, default_fai, default_flank_length)

    def _find_output_art(self, input_art):
        return [o.get('uri') for i, o in self.process.input_output_maps if
                i.get('limsid') == input_art.id and o.get('output-generation-type') == 'PerInput']

    def _upload_genotyping_for_one_sample(self, artifact):
        lims_sample = artifact.samples[0]
        vcf_file = self.geno_conv.generate_vcf(lims_sample.name)
        nb_call = self.geno_conv.nb_calls(lims_sample.name)
        output_arts = self._find_output_art(artifact)
        # there should only be one
        assert len(output_arts) == 1
        # upload the number of calls to output
        output_arts[0].udf[output_genotype_udf_number_call] = nb_call
        output_arts[0].put()

        # and the vcf file
        lims_file = self.lims.upload_new_file(lims_sample, vcf_file)
        # increment the nb of tries
        if submitted_nb_genotype_tries not in lims_sample.udf:
            lims_sample.udf[submitted_nb_genotype_tries] = 1
        else:
            lims_sample.udf[submitted_nb_genotype_tries] += 1

        if submitted_genotype_udf_number_call not in lims_sample.udf:
            # This is the first genotyping results
            lims_sample.udf[submitted_genotype_udf_number_call] = nb_call
            lims_sample.udf[genotype_udf_file_id] = lims_file.id
        elif lims_sample.udf.get(submitted_genotype_udf_number_call) and \
                nb_call > lims_sample.udf.get(submitted_genotype_udf_number_call):
            # This genotyping is better than before
            lims_sample.udf[submitted_genotype_udf_number_call] = nb_call
            lims_sample.udf[genotype_udf_file_id] = lims_file.id
        else:
            self.info(
                'Sample %s new genotype has %s call(s), previous genotype has %s call(s)',
                lims_sample.name,
                nb_call,
                lims_sample.udf[submitted_genotype_udf_number_call]
            )
        # finally upload the submitted samples
        lims_sample.put()
        remove(vcf_file)

    def _run(self):
        invalid_lims_samples = []
        valid_samples = []
        genotyping_samples_used = []

        # First check that all samples are present and matching
        self.info('Matching %s samples from file against %s artifacts',
                  len(self.geno_conv.sample_names), len(self.artifacts))
        for artifact in self.artifacts:
            # Assume only one sample per artifact
            lims_sample = artifact.samples[0]
            if lims_sample.name not in self.geno_conv.sample_names:
                self.info('No match found for %s', lims_sample.name)
                invalid_lims_samples.append(lims_sample)
            else:
                self.info('Matching %s', lims_sample.name)
                genotyping_samples_used.append(lims_sample.name)
                valid_samples.append(lims_sample)

        unused_samples = set(self.geno_conv.sample_names).difference(set(genotyping_samples_used))

        self.info('Matched and uploaded %s artifacts against %s genotype results', len(set(valid_samples)),
                  len(set(genotyping_samples_used)))
        self.info('%s artifacts did not match', len(set(invalid_lims_samples)))
        self.info('%s genotyping results were not used', len(unused_samples))

        # Message to print to stdout if there are missing samples
        messages = []
        if invalid_lims_samples:
            messages.append('%s Samples are missing genotype' % len(invalid_lims_samples))
        if len(self.geno_conv.sample_names) - len(valid_samples) > 0:
            messages.append(
                '%s genotypes have not been assigned' % (len(self.geno_conv.sample_names) - len(valid_samples)))

        if messages:
            # TODO send a message to the EPP
            print(', '.join(messages))
            sys.exit(1)

        # All samples are present and matching: upload all samples
        for artifact in self.artifacts:
            self._upload_genotyping_for_one_sample(artifact)


def main():
    args = _parse_args()
    action = UploadVcfToSamples(args.step_uri, args.username, args.password, args.log_file, args.input_genotypes)
    action.run()


def _parse_args():
    p = step_argparser()
    p.add_argument('--input_genotypes', dest='input_genotypes', type=str, nargs='+',
                   help='The files or artifact id that contains the genotype for all the samples')
    return p.parse_args()


if __name__ == '__main__':
    main()
