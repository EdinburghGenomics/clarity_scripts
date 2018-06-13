#!/usr/bin/env python
import platform
from EPPs.common import step_argparser, SendMailEPP
from EPPs.config import load_config


class ReceiveSampleEmail(SendMailEPP):
    """Notifies the relevant teams that samples for a project have been received"""
    def __init__(self, step_uri, username, password, upl=False):
        super().__init__(step_uri, username, password)
        self.upl = upl

    def _run(self):

        if self.upl==True:
            type='libraries'
            subject_type='Library'
        else:
            type='sample(s)'
            subject_type='Sample'
        if len(self.projects) > 1:
            raise ValueError('More than one project present in step. Only one project per step permitted')

        msg = 'Hi,\n\n{sample_count} {msg_type} have been received for {project} at:\n\n{link}\n\nKind regards,\nClarityX'
        msg = msg.format(
            link='https://' + platform.node() + '/clarity/work-details/' + self.step_id[3:],
            sample_count=len(self.samples),
            msg_type = type,
            project=self.projects[0].name
        )
        subject = self.projects[0].name + ': %s Plate Received' % (subject_type)
        self.send_mail(subject, msg, config_name='projects-facility-lab-finance_only')


def main():
    p = step_argparser()
    p.add_argument('-r', '--upl', action='store_true', help='send upl receipt email', default=False)
    args = p.parse_args()
    load_config()

    action = ReceiveSampleEmail(args.step_uri, args.username, args.password, args.upl)
    action.run()


if __name__ == '__main__':
    main()
