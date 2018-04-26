#!/usr/bin/env python
import platform
from EPPs.common import step_argparser, SendMailEPP
from EPPs.config import load_config


class DataReleaseFMEmail(SendMailEPP):

    def _run(self):
        if len(self.projects)>1: #  check if more than one project in step, only one permitted
            raise ValueError('More than one project present in step. Only one project per step permitted')

        # Create the message
        msg = 'Hi Facility Manager,\n\nThe data for {sample_count} sample(s) is ready to be released for {project}. Please can you perform the following tasks:\n' \
              '\n1) Review the list of samples at:\n{link}\n' \
              '\n2) Provide electronic signature\n' \
              '\n3) Click "Next Steps\n' \
              '\nKind regards,\nClarity X'

        # fill in message with parameters
        msg = msg.format(
            link='https://'+platform.node() + '/clarity/work-details/' + self.step_id[3:],
            sample_count=len(self.samples),
            project=self.projects[0].name,
        )
        subject = self.projects[0].name + ': Review Data for Release'

        # Send email to list of persons specified in the projects-facility-lab-finance_only section of config
        self.send_mail(subject, msg, config_name='projects-facility')


def main():
    # Ge the default command line options
    p = step_argparser()

    # Parse command line options
    args = p.parse_args()

    # Load the config from the default location
    load_config()

    # Setup the EPP
    action = DataReleaseFMEmail(
        args.step_uri, args.username, args.password, args.log_file,
    )

    # Run the EPP
    action.run()


if __name__ == "__main__":
    main()