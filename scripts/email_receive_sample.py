#!/usr/bin/env python
import platform
from EPPs.common import SendMailEPP


class ReceiveSampleEmail(SendMailEPP):
    """Notifies the relevant teams that samples for a project have been received"""
    def __init__(self, argv=None):
        super().__init__(argv)
        self.upl = self.cmd_args.upl

    @staticmethod
    def add_args(argparser):
        argparser.add_argument('-r', '--upl', action='store_true', help='Send UPL receipt email', default=False)

    def _run(self):
        if self.upl:
            msg_type = 'libraries'
            subject_type = 'Library'
        else:
            msg_type = 'sample(s)'
            subject_type = 'Sample'

        if len(self.projects) > 1:
            raise ValueError('More than one project present in step. Only one project per step permitted')

        msg = 'Hi,\n\n{sample_count} {msg_type} have been received for {project} at:\n\n{link}\n\nKind regards,\nClarityX'
        msg = msg.format(
            link='https://' + platform.node() + '/clarity/work-details/' + self.step_id[3:],
            sample_count=len(self.samples),
            msg_type=msg_type,
            project=self.projects[0].name
        )
        subject = self.projects[0].name + ': %s Plate Received' % subject_type
        self.send_mail(subject, msg, config_name='projects-facility-lab-finance_only')


if __name__ == '__main__':
    ReceiveSampleEmail().run()
