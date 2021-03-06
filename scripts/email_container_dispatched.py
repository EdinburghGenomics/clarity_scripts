#!/usr/bin/env python
import platform
from EPPs.common import SendMailEPP


class ContainerDispatchComplete(SendMailEPP):
    """Notifies the lab team that a container is ready for dispatch"""
    _max_nb_project = 1
    def _run(self):

        msg = 'Hi,\n\nThe container dispatch has been completed for {project}.\n\n{link}\n\nKind regards,\nClarityX'
        msg = msg.format(
            link='https://' + platform.node() + '/clarity/work-details/' + self.step_id[3:],
            project=self.projects[0].name
        )

        subject = ', '.join(p.name for p in self.projects) + ': Container Dispatched'

        self.send_mail(subject, msg, config_name='projects-lab')


if __name__ == '__main__':
    ContainerDispatchComplete().run()
