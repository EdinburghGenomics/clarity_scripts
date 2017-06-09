#!/usr/bin/env python
from EPPs.common import StepEPP, step_argparser, get_workflow_stage


class AssignWorkflowStage(StepEPP):
    def __init__(self, step_uri, username, password, log_file, workflow_name, stage_name, source, remove=False, only_once=False):
        super().__init__(step_uri, username, password, log_file)
        self.workflow_name = workflow_name
        self.stage_name = stage_name
        self.source = source
        self.remove = remove
        self.only_once = only_once

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


def main():
    p = step_argparser()
    p.add_argument('--workflow', dest='workflow', type=str, required=True,
                   help='The name of the workflow we should route the artifacts to.')
    p.add_argument('--stage', dest='stage', type=str,
                   help='The name of the stage in the workflow we should route the artifacts to.')
    p.add_argument('--source', dest='source', type=str, required=True, choices=['input', 'output', 'submitted'],
                   help='The name of the stage in the workflow we should route the artifacts to.')
    p.add_argument('--only_once', dest='only_once', action='store_true', default=False,
                   help='Prevent the sample that have gone into this workflow to be assigned again.')
    p.add_argument('--remove', dest='remove', action='store_true', default=False,
                   help='Set the script to remove the artifacts instead of queueing.')

    args = p.parse_args()
    action = AssignWorkflowStage(
        args.step_uri, args.username, args.password, args.log_file,
        args.workflow, args.stage, args.source, args.remove, args.only_once
    )
    action.run()


if __name__ == '__main__':
    main()
