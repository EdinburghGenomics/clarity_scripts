#!/usr/bin/env python
import platform
from EPPs.common import SendMailEPP


class ContainerReadyDispatch(SendMailEPP):
    """Notifies the lab team that a container is ready for dispatch"""

    def _run(self):
        if len(self.projects) > 1:
            raise ValueError('More than one project present in step. Only one project per step permitted')

        msg = 'Hi,\n\nA container is ready for dispatch for {project}.\n\nPlease check the Container Shipment Preparation queue.\n\n{link}\n\nKind regards,\nClarityX'
        msg = msg.format(
            link='https://' + platform.node() + '/clarity/',
            project=self.projects[0].name
        )

        subject = ', '.join(p.name for p in self.projects) + ': Container Ready For Dispatch'

        self.send_mail(subject, msg, config_name='projects-lab')


if __name__ == '__main__':
    ContainerReadyDispatch().run()
