#!/usr/bin/env python
import platform
from EPPs.common import SendMailEPP


class ContainerDispatchComplete(SendMailEPP):
    """Notifies the project team and facilities that a container is ready for dispatch"""
    _max_nb_projects = 1

    def _run(self):

        msg = 'Hi,\n\nPlease review the samples in the step below against the Application Form:\n\n{link}\n\nKind regards,\nClarityX'
        msg = msg.format(
            link='https://' + platform.node() + '/clarity/work-complete/' + self.step_id[3:],
            project=self.projects[0].name
        )

        subject = ', '.join(p.name for p in self.projects) + ': Samples ready for review'

        self.send_mail(subject, msg, config_name='projects-facility')


if __name__ == '__main__':
    ContainerDispatchComplete().run()
