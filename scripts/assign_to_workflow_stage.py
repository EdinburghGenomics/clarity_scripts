#!/usr/bin/env python
from EPPs.common import StepEPP, get_workflow_stage


class AssignWorkflowStage(StepEPP):
    def __init__(self, argv=None):
        super().__init__(argv)
        self.workflow_name = self.cmd_args.workflow
        self.stage_name = self.cmd_args.stage
        self.source = self.cmd_args.source
        self.remove = self.cmd_args.remove
        self.only_once = self.cmd_args.only_once

    @staticmethod
    def add_args(argparser):
        argparser.add_argument(
            '--workflow', type=str, required=True, help='The name of the workflow we should route the artifacts to.'
        )
        argparser.add_argument(
            '--stage', type=str, help='The name of the stage in the workflow we should route the artifacts to.'
        )
        argparser.add_argument(
            '--source', type=str, required=True, choices=['input', 'output', 'submitted'],
            help='The name of the stage in the workflow we should route the artifacts to.'
        )
        argparser.add_argument(
            '--remove', action='store_true', default=False,
            help='Set the script to remove the artifacts instead of queueing.'
        )
        argparser.add_argument(
            '--only_once', action='store_true', default=False,
            help='Prevent the sample that have gone into this workflow to be assigned again.'
        )

    def _run(self):
        artifacts = None
        # Get the output artifacts
        if self.source == 'input':
            artifacts = self.process.all_inputs(unique=True, resolve=True)
        elif self.source == 'output':
            artifacts = self.process.all_outputs(unique=True, resolve=True)
        elif self.source == 'submitted':
            artifacts = list(frozenset([s.artifact for a in self.process.all_inputs() for s in a.samples]))
        # Find the workflow stage
        s = self.stage_name if self.stage_name else None
        stage = get_workflow_stage(self.lims, self.workflow_name, s)
        if not stage:
            raise ValueError(
                'Stage specified by workflow: %s and stage: %s does not exist in %s' % (self.workflow_name,
                                                                                        self.stage_name,
                                                                                        self.baseuri)
            )
        if self.only_once:
            artifacts = self.filter_artifacts_has_been_through_stage(artifacts, stage.uri)

        # Route the artifacts if there are any
        if artifacts:
            if self.remove:
                self.lims.route_artifacts(artifacts, stage_uri=stage.uri, unassign=True)
            else:
                self.lims.route_artifacts(artifacts, stage_uri=stage.uri)

    @staticmethod
    def filter_artifacts_has_been_through_stage(artifacts, stage_uri):
        valid_artifacts = []
        for art in artifacts:
            statuses = [status for stage, status, name in art.workflow_stages_and_statuses if stage.uri == stage_uri]
            if 'COMPLETE' not in statuses:
                valid_artifacts.append(art)  # This artifact has not been through this workflow before
        return valid_artifacts


if __name__ == '__main__':
    AssignWorkflowStage().run()
