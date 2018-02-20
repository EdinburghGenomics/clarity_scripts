#!/usr/bin/env python
import platform
from EPPs.common import step_argparser, SendMailEPP
from EPPs.config import load_config


class ReceiveSampleEmail(SendMailEPP):
    """Notifies the relevant teams that samples for a project have been received"""

    def _run(self):
        if len(self.projects) > 1:
            raise ValueError('More than one project present in step. Only one project per step permitted')

        msg = 'Hi,\n\n{sample_count} sample(s) have been received for {project} at:\n\n{link}\n\nKind regards,\nClarityX'
        msg = msg.format(
            link='https://' + platform.node() + '/clarity/work-details/' + self.step_id[3:],
            sample_count=len(self.samples),
            project=self.projects[0].name
        )
        subject = self.projects[0].name + ': Plate Received'
        self.send_mail(subject, msg, config_name='projects-facility-lab-finance_only')


def main():
    p = step_argparser()
    args = p.parse_args()
    load_config()

    action = ReceiveSampleEmail(args.step_uri, args.username, args.password, args.log_file)
    action.run()


if __name__ == '__main__':
    main()
