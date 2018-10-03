#!/usr/bin/env python
import platform

from EPPs.common import SendMailEPP


class SampleDisposalNotificationEmail(SendMailEPP):

    def _run(self):
        if len(self.projects) > 1:  # check if more than one project in step, only one permitted
            raise ValueError('More than one project present in step. Only one project per step permitted')

        # Create the message
        msg = 'Hi,\n\nThe samples at the link below have been approved for disposal by the Facility Manager:\n' \
              '\n{link}\n' \
              '\nKind regards,\nClarity X'

        # fill in message with parameters
        msg = msg.format(
            link='https://' + platform.node() + '/clarity/work-details/' + self.step_id[3:],
            sample_count=len(self.samples),
            project=self.projects[0].name,
        )
        subject = 'Samples Approved For Disposal'

        # Send email to list of persons specified in the projects-facility-lab-finance_only section of config
        self.send_mail(subject, msg, config_name='projects-lab')


if __name__ == '__main__':
    SampleDisposalNotificationEmail().run()
