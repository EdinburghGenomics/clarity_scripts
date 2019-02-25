#!/usr/bin/env python
from EPPs.common import StepEPP, get_workflow_stage
from pyclarity_lims.entities import Protocol


class AssignWorkflow(StepEPP):
    _use_load_config = False  # prevent the loading of the config file
    """
    This script checks the KAPA Next Step udf and assigns the relevant submitted 
    sample either Request Repeats or Sequencing Plate Preparation defined by the arguments (or does not assign if udf is
    KAPA Make Normalised Libraries 
    """
    def __init__(self, argv=None):
        super().__init__(argv)
        self.sppw = self.cmd_args.sppw
        self.spps = self.cmd_args.spps
        self.rrw = self.cmd_args.rrw
        self.rrs = self.cmd_args.rrs
        self.qw = self.cmd_args.qpcrw
        self.qs = self.cmd_args.qpcrs


    @staticmethod
    def add_args(argparser):
        argparser.add_argument('-sw', '--sppw', type=str, required=True, help='Sequencing plate prepration workflow name')
        argparser.add_argument('-ss', '--spps',  type=str, required=True, help='Sequencing plate preparation step name')
        argparser.add_argument('-rw', '--rrw', type=str, required=True, help='Request repeats workflow name')
        argparser.add_argument('-rs', '--rrs',  type=str, required=True, help='Request repeats step name')
        argparser.add_argument('-qw', '--qpcrw', type=str, required=True, help='Make and Read QPCR workflow name')
        argparser.add_argument('-qs', '--qpcrs',  type=str, required=True, help='Make and Read QPCR step name')


    def _run(self):
        # obtain the actions of the step then creates a StepActions entity for the current step
        actions = self.process.step.actions

        # obtain the next actions in the step then creates a list of dict for next_actions for the step
        next_actions = actions.next_actions

        artifacts_to_route_spp=set()
        artifacts_to_route_rr=set()
        artifacts_to_route_q=set()

        for next_action in next_actions:
            #check to see if next action is removed for the input artifact and then check to see if the artifact should be assigned to Sequencing
            #Plate Preparation, Request Repeats or Make and Read QPCR
            if next_action['action'] == 'remove':
                if next_action['artifact'].udf.get('KAPA Next Step') == 'Sequencing Plate Preparation':
                    artifacts_to_route_spp.add(next_action['artifact'].samples[0].artifact)
                # if KAPA Next Step is Sequencing Plate Preparation then assign to workflow and step defined by rrw and rrs
                elif next_action['artifact'].udf.get('KAPA Next Step') == 'Request Repeats':
                    artifacts_to_route_rr.add(next_action['artifact'].samples[0].artifact)
                elif next_action['artifact'].udf.get('KAPA Next Step') == 'Make and Read qPCR Quant':
                    artifacts_to_route_q.add(next_action['artifact'].samples[0].artifact)

        #if any artifacts with Sequencing Plate Preparation then assign to workflow and step for sequencing plate preparation
        if artifacts_to_route_spp:
            stage = get_workflow_stage(self.lims, self.sppw, self.spps)
            self.lims.route_artifacts(list(artifacts_to_route_spp), stage_uri=stage.uri)

        #if any artifacts with Request Repeats then assign to workflow and step for request repeats
        if artifacts_to_route_rr:
            stage = get_workflow_stage(self.lims, self.rrw, self.rrs)
            self.lims.route_artifacts(list(artifacts_to_route_rr), stage_uri=stage.uri)

        #if any artifacts with Make and Read QPCR then assign to workflow and step for Make and Read QCPR (could not achieve this with the next_action re-work)
        if artifacts_to_route_q:
            stage = get_workflow_stage(self.lims, self.qw, self.qs)
            self.lims.route_artifacts(list(artifacts_to_route_q), stage_uri=stage.uri)


if __name__ == '__main__':
    AssignWorkflow().run()
