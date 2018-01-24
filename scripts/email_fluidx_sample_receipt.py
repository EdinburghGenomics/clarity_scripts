#!/usr/bin/env python
from collections import defaultdict
import platform
from EPPs.common import step_argparser, SendMailEPP
from EPPs.config import load_config


class FluidXSampleReceiptEmail(SendMailEPP):

    def _run(self):
        if len(self.projects)>1: #check if more than one project in step, only one permitted
            raise ValueError('More than one project present in step. Only one project per step permitted')



        # Create the message to notify the lab team, projects and finance that samples have arrived at the facility


        msg = 'Hi,\n\n{sample_count} sample(s) have been received for project {project} at:\n\n{link}\n\nKind regards,\nClarityX'

        # fill in message with parameters
        msg = msg.format(
            link='https://'+platform.node() + '/clarity/work-details/' + self.step_id[3:],
            sample_count=len(self.samples),
            project=self.samples[0].project.name,
        )
        subject = ', '.join([p.name for p in self.projects]) + ': FluidX Tube Received'


        # Send email to list of persons specified in the default section of config
        self.send_mail(subject, msg, config_name='projects-lab-finance_only')

        # Alternatively You can send the email to specific section of config
        #self.send_mail(subject, msg, config_name='project_only')

        # Create the message to request manifest parsing by the project team

        msg2 = 'Hi,\n\nThe manifest should now be parsed for project {project} go to the queue for step FluidX Manifest Parsing EG 1.0 ST at:\
                \n\n{link}\n\nKind regards,\nClarityX'

        # fill in message with parameters
        msg2 = msg2.format(
            link='https://' + platform.node() + '/clarity/queue/752',
            project=self.samples[0].project.name,
        )
        subject2 = ', '.join([p.name for p in self.projects]) + ': Parse Manifest Required (FluidX)'
        self.send_mail(subject2, msg2, config_name='projects_only')

def main():
    # Ge the default command line options
    p = step_argparser()

    # Parse command line options
    args = p.parse_args()

    # Load the config from the default location
    load_config()

    # Setup the EPP
    action = FluidXSampleReceiptEmail(
        args.step_uri, args.username, args.password, args.log_file,
    )

    # Run the EPP
    action.run()


if __name__ == "__main__":
    main()