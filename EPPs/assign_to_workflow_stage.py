from EPPs.common import EPP, argparser, get_workflow_stage


class AssignWorkflowStage(EPP):
    def __init__(self, step_uri, username, password, workflow_name, stage_name, source):
        super().__init__(step_uri, username, password)
        self.workflow_name = workflow_name
        self.stage_name = stage_name
        self.source = source

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
                'Stage specified by workflow: %s and stage: %s does not exist in %s' % (self.workflow_name, self.stage_name, self.baseuri)
            )
        # Route the artifacts
        self.lims.route_artifacts(artifacts, stage_uri=stage.uri)


def main():
    p = argparser()
    p.add_argument('--workflow', dest='workflow', type=str, required=True,
                   help='The name of the workflow we should route the artifacts to.')
    p.add_argument('--stage', dest='stage', type=str,
                   help='The name of the stage in the workflow we should route the artifacts to.')
    p.add_argument('--source', dest='source', type=str, required=True, choices=['input', 'output', 'submitted'],
                   help='The name of the stage in the workflow we should route the artifacts to.')

    args = p.parse_args()
    action = AssignWorkflowStage(args.step_uri, args.username, args.password, args.workflow, args.stage, args.source)
    action.run()


if __name__ == '__main__':
    main()
