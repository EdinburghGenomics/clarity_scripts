#!/usr/bin/env python
import platform
from EPPs.common import step_argparser, SendMailEPP
from EPPs.config import load_config


class FluidXSampleReceiptEmail(SendMailEPP):
    """Sends an email to request FluidX manifest parsing by the project team"""

    def _run(self):
        if len(self.projects) > 1:
            raise ValueError('More than one project present in step. Only one project per step permitted')

        msg = 'Hi,\n\n{sample_count} sample(s) have been received for project {project} at:\n\n{link}\n\nKind regards,\nClarityX'
        msg = msg.format(
            link='https://' + platform.node() + '/clarity/work-details/' + self.step_id[3:],
            sample_count=len(self.samples),
            project=self.projects[0].name,
        )
        subject = ', '.join(p.name for p in self.projects) + ': FluidX Tube Received'

        self.send_mail(subject, msg, config_name='projects-lab-finance_only')

        msg2 = '''Hi,

The manifest should now be parsed for project {project} go to the queue for step FluidX Manifest Parsing EG 1.0 ST at:

{link}

Kind regards,
ClarityX'''

        msg2 = msg2.format(link='https://' + platform.node() + '/clarity/queue/752', project=self.projects[0].name)
        subject2 = ', '.join(p.name for p in self.projects) + ': Parse Manifest Required (FluidX)'
        self.send_mail(subject2, msg2, config_name='projects_only')


def main():
    p = step_argparser()
    args = p.parse_args()
    load_config()

    action = FluidXSampleReceiptEmail(args.step_uri, args.username, args.password, args.log_file)
    action.run()


if __name__ == '__main__':
    main()
