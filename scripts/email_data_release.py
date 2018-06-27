#!/usr/bin/env python
import platform
from EPPs.common import SendMailEPP


class DataReleaseEmail(SendMailEPP):
    """
    Notifies the relevant teams that data for a project has been released. Also sends a reminder to send a customer
    survey depending on UDF values.
    """

    def _run(self):
        if len(self.projects) > 1:
            raise ValueError('More than one project present in step. Only one project per step permitted')

        msg = 'Hi,\n\nData for {sample_count} sample(s) has been released for {project} at:\n\n{link}\n\nKind regards,\nClarityX'
        msg = msg.format(
            link='https://' + platform.node() + '/clarity/work-details/' + self.step_id[3:],
            sample_count=len(self.samples),
            project=self.projects[0].name
        )
        subject = ', '.join(p.name for p in self.projects) + ': Data Released'
        self.send_mail(subject, msg, config_name='projects-facility-finance_only')

        if self.process.udf.get('Request Customer Survey (Final Data Release)') == 'Yes':
            msg2 = 'Hi,\n\nThe final data release has occurred for {project}. Please request a customer survey.\n\nKind regards,\nClarityX'
            msg2 = msg2.format(project=self.projects[0].name)

            subject2 = self.projects[0].name + ': Request Customer Survey - Final Data Released'
            self.send_mail(subject2, msg2, config_name='projects-facility-finance-bd_only')


if __name__ == '__main__':
    DataReleaseEmail().run()
