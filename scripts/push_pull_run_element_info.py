#!/usr/bin/env python
import datetime

from cached_property import cached_property
from egcg_core import rest_communication

from EPPs.common import StepEPP, step_argparser
from EPPs.config import load_config

reporting_app_date_format = '%d_%m_%Y_%H:%M:%S'

metrics_mapping_pull = [
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

class PullRunElementInfo(StepEPP):

    def output_artifacts_per_sample(self, sample_name):
        return [
            io[1]['uri']
            for io in self.process.input_output_maps
            if io[0]['uri'].samples[0].name == sample_name and io[1]['output-type'] == 'ResultFile'
        ]


    def _run(self):
        artifacts_to_upload = set()
        # batch retrieve input and output artifacts along with samples
        self.output_artifacts
        for sample in self.samples:
            run_elements = rest_communication.get_documents('aggregate/run_elements', match={'sample_id': sample.name})
            artifacts = self.output_artifacts_per_sample(sample_name=sample.name)
            assert len(run_elements) == len(artifacts)
            for i in range(len(run_elements)):
                for art_field, re_field in metrics_mapping_pull:
                    value = run_elements[i].get(re_field)
                    if value is not None:
                        if re_field.endswith('date'):
                            value = datetime.datetime.strptime(value, reporting_app_date_format).strftime('%Y-%m-%d')
                        artifacts[i].udf[art_field] = value

                        artifacts_to_upload.add(artifacts[i])
            self.assess_sample(sample)
        self.lims.put_batch(artifacts_to_upload)

    def assess_sample(self, sample):
        artifacts = self.output_artifacts_per_sample(sample_name=sample.name)
        un_reviewed_artifacts = [a for a in artifacts if a.udf.get('RE Review status') not in ['pass', 'fail']]
        if un_reviewed_artifacts:
            # Skip sample that have some un-reviewed run elements as they could still be sequencing and change the outcome of the review
            return

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

        # Not enough good yield: manual decision
        # Run element not passing review: manual decision

metrics_mapping_push = [
    ('RE Useable', 'useable'),
    ('RE Useable Comment', 'useable_comments'),
]

class PushRunElementInfo(StepEPP):

    @cached_property
    def now(self):
        return datetime.datetime.now()

    def output_artifacts_per_sample(self, sample_name):
        return [
            io[1]['uri']
            for io in self.process.input_output_maps
            if io[0]['uri'].samples[0].name == sample_name and io[1]['output-type'] == 'ResultFile'
        ]


    def _run(self):
        # batch retrieve input and output artifacts along with samples
        self.output_artifacts
        for sample in self.samples:
            run_elements = rest_communication.get_documents('aggregate/run_elements', match={'sample_id': sample.name})
            run_elements_dict = {}
            for run_element in run_elements:
                run_elements_dict[run_element['run_element_id']] = run_element
            artifacts = self.output_artifacts_per_sample(sample_name=sample.name)
            assert len(run_elements) == len(artifacts)
            for artifact in artifacts:
                run_element = run_elements_dict.get(artifact.udf.get('RE Id'))
                run_element_to_upload = {}
                for art_field, re_field in metrics_mapping_push:
                    value = artifact.udf.get(art_field)
                    if value is not None and value != run_element.get(re_field):
                        run_element_to_upload[re_field] = value

                if run_element_to_upload:
                    # The date is set to now.
                    run_element_to_upload['useable_date'] = self.now.strftime(reporting_app_date_format)
                    rest_communication.patch_entry('run_elements', run_element_to_upload, 'run_element_id', artifact.udf.get('RE Id'))

        # finish the action on the rest api
        rest_communication.patch_entry(
            'actions',
            {'date_finished': self.now.strftime(reporting_app_date_format)},
            'action_id',
            'lims_' + self.process.id
        )

def main():
    p = step_argparser()
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument('--push', action='store_true')
    group.add_argument('--pull', action='store_true')

    load_config()

    args = p.parse_args()
    if args.push:
        action = PushRunElementInfo(
            args.step_uri, args.username, args.password, args.log_file
        )
    elif args.pull:
        action = PullRunElementInfo(
            args.step_uri, args.username, args.password, args.log_file
        )

    action.run()


if __name__ == '__main__':
    main()
