#!/usr/bin/env python
import datetime
from egcg_core import util
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

    def check_rest_data_and_artifacts(self, sample_name):
        query_args = {'where': {'sample_id': sample_name}}
        rest_entities = self.get_documents(self.endpoint, **query_args)
        artifacts = self.output_artifacts_per_sample(sample_name=sample_name)
        if len(rest_entities) != len(artifacts):  # in sample review this will be 1, in run review this will be more
            raise AssertionError(
                'Data mismatch for sample %s: got %s Rest entities, %s output artifacts' % (
                    sample_name, len(rest_entities), len(artifacts)
                )
            )
        return rest_entities, artifacts

    def delivered(self, sample_name):
        d = {'yes': True, 'no': False}
        query_args = {'where': {'sample_id': sample_name}}
        sample = self.get_documents('samples', **query_args)[0]
        return d.get(sample.get('delivered'))

    def processed(self, sample_name):
        query_args = {'where': {'sample_id': sample_name}}
        sample = self.get_documents('samples', **query_args)[0]
        processing_status = util.query_dict(sample, 'aggregated.most_recent_proc.status')
        return processing_status == 'finished'

    def _run(self):
        raise NotImplementedError


class PullInfo(StepPopulator):
    def __init__(self, step_uri, username, password, log_file=None, pull_data=True):
        super().__init__(step_uri, username, password, log_file)
        self.pull_data = pull_data

    def _run(self):
        artifacts_to_upload = set()
        _ = self.output_artifacts  # batch retrieve input and output artifacts along with samples
        for sample in self.samples:
            if self.pull_data:
                self.debug('Adding artifact info for %s', sample.name)
                artifacts_to_upload.update(self.add_artifact_info(sample))
            self.debug('Assessing sample %s', sample.name)
            artifacts_to_upload.update(self.assess_sample(sample))
        self.lims.put_batch(artifacts_to_upload)

    def add_artifact_info(self, sample):
        rest_entities, artifacts = self.check_rest_data_and_artifacts(sample.name)
        artifacts_to_upload = set()
        for i in range(len(rest_entities)):
            for art_field, api_field in self.metrics_mapping:
                value = self.field_from_entity(rest_entities[i], api_field)
                if value is not None:
                    if api_field.endswith('date'):
                        value = datetime.datetime.strptime(value, reporting_app_date_format).strftime('%Y-%m-%d')
                    artifacts[i].udf[art_field] = value
                    artifacts_to_upload.add(artifacts[i])

        return artifacts_to_upload

    def field_from_entity(self, entity, api_field):
        return util.query_dict(entity, api_field)

    def assess_sample(self, sample):
        raise NotImplementedError


class PullRunElementInfo(PullInfo):
    endpoint = 'run_elements'
    metrics_mapping = [
        ('RE Id', 'run_element_id'),
        ('RE Nb Reads', 'passing_filter_reads'),
        ('RE Yield', 'aggregated.clean_yield_in_gb'),
        ('RE Yield Q30', 'aggregated.clean_yield_q30_in_gb'),
        ('RE %Q30', 'aggregated.clean_pc_q30'),
        ('RE Coverage', 'coverage.mean'),
        ('RE Estimated Duplicate Rate', 'lane_pc_optical_dups'),
        ('RE %Adapter', 'aggregated.pc_adaptor'),
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
        # Artifacts that are new
        new_artifacts = [a for a in artifacts if a.udf.get('RE previous Useable') not in ['yes', 'no']]

        # skip samples which have been delivered, mark any new REs as such, not changing older RE comments
        if self.delivered(sample.name):
            for a in new_artifacts:
                a.udf['RE Useable Comment'] = 'AR: Delivered'
                a.udf['RE Useable'] = 'no'

            for a in pass_artifacts + fail_artifacts:
                if a.udf.get('RE previous Useable Comment') and a.udf.get('RE previous Useable'):
                    a.udf['RE Useable Comment'] = a.udf.get('RE previous Useable Comment')
                    a.udf['RE Useable'] = a.udf.get('RE previous Useable')

            artifacts_to_upload.update(artifacts)
            return artifacts_to_upload

        # skip samples which have been processed, mark any new REs as such, not changing older RE comments
        if self.processed(sample.name):
            for a in pass_artifacts + fail_artifacts:
                if a.udf.get('RE previous Useable Comment') and a.udf.get('RE previous Useable'):
                    a.udf['RE Useable Comment'] = a.udf.get('RE previous Useable Comment')
                    a.udf['RE Useable'] = a.udf.get('RE previous Useable')

            for a in new_artifacts:
                a.udf['RE Useable Comment'] = 'AR: Sample already processed'
                a.udf['RE Useable'] = 'no'

            artifacts_to_upload.update(artifacts)
            return artifacts_to_upload

        target_yield = float(sample.udf.get('Required Yield (Gb)'))
        good_re_yield = sum([float(a.udf.get('RE Yield')) for a in pass_artifacts])

        # Increase target coverage by 5% to resolve borderline cases
        target_coverage = 1.05 * sample.udf.get('Coverage (X)')
        obtained_coverage = float(sum([a.udf.get('RE Coverage') for a in pass_artifacts]))

        # Too much good yield limit to the best quality ones
        if good_re_yield > target_yield * 2 and obtained_coverage > target_coverage:
            # Too much yield: sort the good artifact by quality
            pass_artifacts.sort(key=lambda x: x.udf.get('RE %Q30'), reverse=True)
            current_yield = 0
            for a in pass_artifacts:
                current_yield += float(a.udf.get('RE Yield'))
                if current_yield < target_yield * 2:
                    a.udf['RE Useable'] = 'yes'
                    a.udf['RE Useable Comment'] = 'AR: Good yield'
                else:
                    a.udf['RE Useable'] = 'no'
                    a.udf['RE Useable Comment'] = 'AR: Too much good yield'
            for a in fail_artifacts:
                a.udf['RE Useable'] = 'no'
                a.udf['RE Useable Comment'] = 'AR: Failed and not needed'
            artifacts_to_upload.update(artifacts)

        # Just the right amount of good yield: take it all
        elif target_yield < good_re_yield < target_yield * 2 or obtained_coverage > target_coverage:
            for a in pass_artifacts:
                a.udf['RE Useable'] = 'yes'
                a.udf['RE Useable Comment'] = 'AR: Good yield'
            for a in fail_artifacts:
                a.udf['RE Useable'] = 'no'
                a.udf['RE Useable Comment'] = 'AR: Failed and not needed'
            artifacts_to_upload.update(artifacts)

        # Not enough good yield: manual decision
        # Run element not passing review: manual decision

        return artifacts_to_upload


class PullSampleInfo(PullInfo):
    endpoint = 'samples'
    metrics_mapping = [
        ('SR Yield (Gb)', 'aggregated.clean_yield_in_gb'),
        ('SR %Q30', 'aggregated.clean_pc_q30'),
        ('SR % Mapped', 'aggregated.pc_mapped_reads'),
        ('SR % Duplicates', 'aggregated.pc_duplicate_reads'),
        ('SR Mean Coverage', 'aggregated.mean_coverage'),
        ('SR Species Found', 'aggregated.matching_species'),
        ('SR Sex Check Match', 'aggregated.gender_match'),
        ('SR Genotyping Match', 'aggregated.genotype_match'),
        ('SR Freemix', 'sample_contamination.freemix'),
        ('SR Review Status', 'reviewed'),
        ('SR Review Comments', 'review_comments'),
        ('SR Review Date', 'review_date'),
        ('SR previous Useable', 'useable'),
        ('SR previous Useable Comments', 'useable_comments'),
        ('SR previous Useable Date', 'useable_date')
    ]

    def assess_sample(self, sample):
        artifacts = self.output_artifacts_per_sample(sample_name=sample.name)
        un_reviewed_artifacts = [a for a in artifacts if a.udf.get('SR Review Status') not in ['pass', 'fail']]
        if un_reviewed_artifacts:
            # Skip unreviewed samples
            return artifacts

        for a in artifacts:
            if a.udf.get('SR Review Status') == 'pass':
                a.udf['SR Useable'] = 'yes'
                a.udf['SR Useable Comments'] = 'AR: Review passed'

            elif a.udf.get('SR Review Status') == 'fail':
                a.udf['SR Useable'] = 'no'
                a.udf['SR Useable Comments'] = 'AR: Review failed'

        return artifacts

    def field_from_entity(self, entity, api_field):
        field = super().field_from_entity(entity, api_field)
        if api_field == 'aggregated.matching_species':
            return ', '.join(field)
        return field


class PushInfo(StepPopulator):
    api_id_field = None

    def review_entity_uid(self, artifact):
        raise NotImplementedError

    @cached_property
    def current_time(self):
        return datetime.datetime.now().strftime(reporting_app_date_format)

    def _run(self):
        # batch retrieve input and output artifacts along with samples
        _ = self.output_artifacts
        for sample in self.samples:
            self.info('Pushing data for sample %s', sample.name)
            rest_entities, artifacts = self.check_rest_data_and_artifacts(sample.name)
            rest_api_data = {}
            for e in rest_entities:
                rest_api_data[e[self.api_id_field]] = e

            for artifact in artifacts:
                rest_entities = rest_api_data.get(self.review_entity_uid(artifact))
                payload = {}
                for art_field, api_field in self.metrics_mapping:
                    value = artifact.udf.get(art_field)
                    if value is not None and value != rest_entities.get(api_field):
                        payload[api_field] = value

                if payload:
                    # The date is set to now.
                    payload['useable_date'] = self.current_time
                    self.patch_entry(self.endpoint, payload, self.api_id_field, self.review_entity_uid(artifact))

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
    metrics_mapping = [
        ('RE Useable', 'useable'),
        ('RE Useable Comment', 'useable_comments'),
    ]

    def review_entity_uid(self, artifact):
        return artifact.udf.get('RE Id')


class PushSampleInfo(PushInfo):
    endpoint = 'samples'
    api_id_field = 'sample_id'
    metrics_mapping = [
        ('SR Useable', 'useable'),
        ('SR Useable Comments', 'useable_comments'),
    ]

    def review_entity_uid(self, artifact):
        return artifact.samples[0].name


def main():
    p = step_argparser()
    p.add_argument('--review_type', required=True, choices=('run', 'sample'))
    p.add_argument('--action_type', required=True, choices=('pull', 'push'))
    p.add_argument('--assess_only', action='store_true')

    load_config()
    args = p.parse_args()

    cls_args = [args.step_uri, args.username, args.password, args.log_file]
    if args.assess_only:
        assert args.action_type == 'pull'
        cls_args.append(False)

    reviewer_map = {
        'run': {'pull': PullRunElementInfo, 'push': PushRunElementInfo},
        'sample': {'pull': PullSampleInfo, 'push': PushSampleInfo}
    }
    action = reviewer_map[args.review_type][args.action_type](*cls_args)
    action.run()


if __name__ == '__main__':
    main()
