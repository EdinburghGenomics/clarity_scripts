#!/usr/bin/env python
import platform

from EPPs.common import SendMailEPP


class SampleDisposalNotificationEmail(SendMailEPP):

    def _run(self):

        # Create the message
        msg = 'Hi,\n\nThe samples at the link below have been approved for disposal by the Facility Manager:\n' \
              '\n{link}\n' \
              '\nKind regards,\nClarity X'

        # fill in message with parameters
        msg = msg.format(
            link='https://' + platform.node() + '/clarity/work-details/' + self.step_id[3:],
        )
        subject = 'Samples Approved For Disposal'

        # Send email to list of persons specified in the projects-facility-lab-finance_only section of config
        self.send_mail(subject, msg, config_name='projects-lab')


if __name__ == '__main__':
    SampleDisposalNotificationEmail().run()
