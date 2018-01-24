#!/usr/bin/env python
from collections import defaultdict
import platform
from EPPs.common import step_argparser, SendMailEPP
from EPPs.config import load_config


class DataReleaseEmail(SendMailEPP):

    def _run(self):
        if len(self.projects)>1: #check if more than one project in step, only one permitted
            raise ValueError('More than one project present in step. Only one project per step permitted')



        # Create the message to notify team that dat has been released


        msg = 'Hi,\n\nData for {sample_count} sample(s) has been released for {project} at:\n\n{link}\n\nKind regards,\nClarityX'

        # fill in message with parameters
        msg = msg.format(
            link='https://'+platform.node() + '/clarity/work-details/' + self.step_id[3:],
            sample_count=len(self.samples),
            project=self.samples[0].project.name,
        )
        subject = ', '.join([p.name for p in self.projects]) + ': Data Released'

        # Send email to list of persons specified in the default section of config
        self.send_mail(subject, msg, config_name='projects-facility-finance_only')

        # Alternatively You can send the email to specific section of config
        #self.send_mail(subject, msg, config_name='project_only')

        #if "Request Customer Survey (Final Data Release)" step UDF completed as "Yes" send an additional email to notify business team to send customer survey
        # and reminder to finance that the final release has occurred
        if self.process.udf.get("Request Customer Survey (Final Data Release)") == "Yes":
            msg2 = 'Hi,\n\nThe final data release has occurred for {project}. Please request a customer survey.\n\nKind regards,\nClarityX'

            # fill in message with parameters
            msg2 = msg2.format(
                link='https://'+platform.node() + '/clarity/work-details/' + self.step_id[3:],
                sample_count=len(self.samples),
                project=self.samples[0].project.name,
            )
            subject2 = ', '.join([p.name for p in self.projects]) + ': Request Customer Survey - Final Data Released'
            self.send_mail(subject2, msg2, config_name='projects-facility-finance-bd_only')

def main():
    # Ge the default command line options
    p = step_argparser()

    # Parse command line options
    args = p.parse_args()

    # Load the config from the default location
    load_config()

    # Setup the EPP
    action = DataReleaseEmail(
        args.step_uri, args.username, args.password, args.log_file,
    )

    # Run the EPP
    action.run()


if __name__ == "__main__":
    main()