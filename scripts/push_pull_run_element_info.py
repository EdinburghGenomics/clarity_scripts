#!/usr/bin/env python
import datetime
from cached_property import cached_property
from EPPs.common import StepEPP, RestCommunicationEPP, step_argparser
from EPPs.config import load_config

reporting_app_date_format = '%d_%m_%Y_%H:%M:%S'


class StepPopulator(StepEPP, RestCommunicationEPP):
    metrics_mapping = {}
    endpoint = None

    def output_artifacts_per_sample(self, sample_name):
        return [
            io[1]['uri']
            for io in self.process.input_output_maps
            if io[0]['uri'].samples[0].name == sample_name and io[1]['output-type'] == 'ResultFile'
        ]

    def _run(self):
        raise NotImplementedError


class PullInfo(StepPopulator):
    def __init__(self, step_uri, username, password, log_file=None, pull_data=True):
        super().__init__(step_uri, username, password, log_file)
        self.pull_data = pull_data

    def _run(self):
        artifacts_to_upload = set()
        # batch retrieve input and output artifacts along with samples
        _ = self.output_artifacts
        for sample in self.samples:
            if self.pull_data:
                artifacts_to_upload.update(self.add_artifact_info(sample))
            artifacts_to_upload.update(self.assess_sample(sample))
        self.lims.put_batch(artifacts_to_upload)

    def add_artifact_info(self, sample):
        run_elements = self.get_documents(self.endpoint, match={'sample_id': sample.name})
        artifacts = self.output_artifacts_per_sample(sample_name=sample.name)
        assert len(run_elements) == len(artifacts)
        artifacts_to_upload = set()
        for i in range(len(run_elements)):
            for art_field, api_field in self.metrics_mapping:
                value = run_elements[i].get(api_field)
                if value is not None:
                    if api_field.endswith('date'):
                        value = datetime.datetime.strptime(value, reporting_app_date_format).strftime('%Y-%m-%d')
                    artifacts[i].udf[art_field] = value
                    artifacts_to_upload.add(artifacts[i])

        return artifacts_to_upload

    def assess_sample(self, sample):
        raise NotImplementedError


class PullRunElementInfo(PullInfo):
    endpoint = 'aggregate/run_elements'
    metrics_mapping = [
        ('RE Id', 'run_element_id'),
        ('RE Nb Reads', 'passing_filter_reads'),
        ('RE Yield', 'clean_yield_in_gb'),
        ('RE Yield Q30', 'clean_yield_q30_in_gb'),
        ('RE %Q30', 'clean_pc_q30'),
        ('RE Estimated Duplicate Rate', 'lane_pc_optical_dups'),
        ('RE %Adapter', 'pc_adapter'),
        ('RE Review status', 'reviewed'),
        ('RE Review Comment', 'review_comments'),
        ('RE Review date', 'review_date'),
        ('RE previous Useable', 'useable'),
        ('RE previous Useable Comment', 'useable_comments'),
        ('RE previous Useable date', 'useable_date')
    ]

    def assess_sample(self, sample):
        artifacts_to_upload = set()

        artifacts = self.output_artifacts_per_sample(sample_name=sample.name)
        un_reviewed_artifacts = [a for a in artifacts if a.udf.get('RE Review status') not in ['pass', 'fail']]
        if un_reviewed_artifacts:
            # Skip samples that have un-reviewed run elements - could still be sequencing and change review outcome
            return artifacts_to_upload

        # Artifacts that pass the review
        pass_artifacts = [a for a in artifacts if a.udf.get('RE Review status') == 'pass']

        # Artifacts that fail the review
        fail_artifacts = [a for a in artifacts if a.udf.get('RE Review status') == 'fail']

        target_yield = float(sample.udf.get('Yield for Quoted Coverage (Gb)'))
        good_re_yield = sum([float(a.udf.get('RE Yield Q30')) for a in pass_artifacts])

        # Just the right amount of good yield: take it all
        if target_yield < good_re_yield < target_yield * 2:
            for a in pass_artifacts:
                a.udf['RE Useable'] = 'yes'
                a.udf['RE Useable Comment'] = 'AR: Good yield'
            for a in fail_artifacts:
                a.udf['RE Useable'] = 'no'
                a.udf['RE Useable Comment'] = 'AR: Failed and not needed'
            artifacts_to_upload.update(artifacts)

        # Too much good yield limit to the best quality ones
        elif good_re_yield > target_yield * 2:
            # Too much yield: sort the good artifact by quality
            pass_artifacts.sort(key=lambda x: x.udf.get('RE %Q30'), reverse=True)
            current_yield = 0
            for a in pass_artifacts:
                current_yield += float(a.udf.get('RE Yield Q30'))
                if current_yield < target_yield * 2:
                    a.udf['RE Useable'] = 'yes'
                    a.udf['RE Useable Comment'] = 'AR: Good yield'
                else:
                    a.udf['RE Useable'] = 'no'
                    a.udf['RE Useable Comment'] = 'AR: To much good yield'
            for a in fail_artifacts:
                a.udf['RE Useable'] = 'no'
                a.udf['RE Useable Comment'] = 'AR: Failed and not needed'
            artifacts_to_upload.update(artifacts)

        # Not enough good yield: manual decision
        # Run element not passing review: manual decision

        return artifacts_to_upload


class PullSampleInfo(PullInfo):
    endpoint = 'aggregate/samples'

    metrics_mapping = [
        ('Sample ID', 'sample_id'),
        ('User Sample ID', 'user_sample_id'),
        ('Sample Yield', 'yield'),
        ('Sample %Q30', 'qc_q30'),
        ('Sample % Mapped', 'pc_mapped'),
        ('Sample % Duplicates', 'pc_duplicates'),
        ('Sample Mean Coverage', 'mean_coverage'),
        ('Sample Species Found', 'species_found'),
        ('Sample Sex Check Match', 'gender_match'),
        ('Sample Genotype Match', 'genotype_match'),
        ('Sample Freemix', 'freemix'),
        ('Sample Review status', 'reviewed'),  # ####
        ('Sample Review Comment', 'review_comments'),
        ('Sample Review date', 'review_date'),
        ('Sample previous Useable', 'useable'),
        ('Sample previous Useable Comment', 'useable_comments'),
        ('Sample previous Useable date', 'useable_date')
    ]

    def assess_sample(self, sample):
        artifacts = self.output_artifacts_per_sample(sample_name=sample.name)
        un_reviewed_artifacts = [a for a in artifacts if a.udf.get('Sample Review status') not in ['pass', 'fail']]
        if un_reviewed_artifacts:
            # Skip unreviewed samples
            return artifacts

        for a in artifacts:
            if a.udf.get('Sample Review status') == 'pass':
                a.udf['Sample Useable'] = 'yes'
                a.udf['Sample Useable Comment'] = 'AR: Review passed'

            elif a.udf.get('Sample Review status') == 'fail':
                a.udf['Sample Useable'] = 'no'
                a.udf['Sample Useable Comment'] = 'AR: Review failed'

        return artifacts


class PushInfo(StepPopulator):
    endpoint = None
    api_id_field = None
    udf_id_field = None

    @cached_property
    def current_time(self):
        return datetime.datetime.now().strftime(reporting_app_date_format)

    def _run(self):
        # batch retrieve input and output artifacts along with samples
        _ = self.output_artifacts
        for sample in self.samples:
            data = self.get_documents('run_elements', where={'sample_id': sample.name})

            rest_api_data = {}
            for d in data:
                rest_api_data[d[self.api_id_field]] = d
            artifacts = self.output_artifacts_per_sample(sample_name=sample.name)
            assert len(data) == len(artifacts)  # for sample review, this will be 1. For run review, this will be more

            for artifact in artifacts:
                data = rest_api_data.get(artifact.udf.get(self.udf_id_field))
                payload = {}
                for art_field, api_field in self.metrics_mapping:
                    value = artifact.udf.get(art_field)
                    if value is not None and value != data.get(api_field):
                        payload[api_field] = value

                if payload:
                    # The date is set to now.
                    payload['useable_date'] = self.current_time
                    self.patch_entry(self.endpoint, payload, self.api_id_field, artifact.udf.get(self.udf_id_field))

        # finish the action on the rest api
        self.patch_entry(
            'actions',
            {'date_finished': self.current_time},
            'action_id',
            'lims_' + self.process.id
        )


class PushRunElementInfo(PushInfo):
    endpoint = 'run_elements'
    api_id_field = 'run_element_id'
    udf_id_field = 'RE Id'
    metrics_mapping = [
        ('RE Useable', 'useable'),
        ('RE Useable Comment', 'useable_comments'),
    ]


class PushSampleInfo(PushInfo):
    endpoint = 'samples'
    api_id_field = 'sample_id'
    udf_id_field = 'Sample ID'
    metrics_mapping = [
        ('Sample Useable', 'useable'),
        ('Sample Useable Comment', 'useable_comments'),
    ]


def main():
    p = step_argparser()
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument('--push', action='store_true')
    group.add_argument('--assess', action='store_true')
    group.add_argument('--pull_and_assess', action='store_true')

    load_config()

    args = p.parse_args()
    if args.push:
        action = PushRunElementInfo(
            args.step_uri, args.username, args.password, args.log_file
        )
    elif args.pull_and_assess:
        action = PullRunElementInfo(
            args.step_uri, args.username, args.password, args.log_file
        )
    elif args.assess:
        action = PullRunElementInfo(
            args.step_uri, args.username, args.password, args.log_file, pull_data=False,
        )

    action.run()


if __name__ == '__main__':
    main()
