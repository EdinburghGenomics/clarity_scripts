#!/usr/bin/env python
import platform

from EPPs.common import SendMailEPP


class SampleDisposalFMEmail(SendMailEPP):

    def _run(self):

        # Create the message
        msg = 'Hi Facility Manager,\n\nSamples are ready for disposal. Please follow the link below and perform the following tasks:\n' \
              '\n1) Review the list of samples at:\n{link}\n' \
              '\n2) Provide electronic signature\n' \
              '\n3) Click "Next Steps\n' \
              '\nKind regards,\nClarity X'

        # fill in message with parameters
        msg = msg.format(
            link='https://' + platform.node() + '/clarity/work-details/' + self.step_id[3:],
            sample_count=len(self.samples),
            project=self.projects[0].name,
        )
        subject = 'Review Samples for Disposal'

        # Send email to list of persons specified in the projects-facility-lab-finance_only section of config
        self.send_mail(subject, msg, config_name='projects-facility')


if __name__ == '__main__':
    SampleDisposalFMEmail().run()
