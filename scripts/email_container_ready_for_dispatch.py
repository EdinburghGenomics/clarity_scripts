#!/usr/bin/env python
import platform

from EPPs.common import SendMailEPP


class ContainerReadyDispatch(SendMailEPP):
    _max_nb_projects = 1
    """Notifies the lab team that a container is ready for dispatch"""

    def _run(self):
        msg = 'Hi,\n\nA container is ready for dispatch for {project}.\n\nCourier: {courier}\n\nPlease check the Container Shipment Preparation queue.\n\n{link}\n\nKind regards,\nClarityX'
        msg = msg.format(
            link='https://' + platform.node() + '/clarity/',
            project=self.projects[0].name,
            courier=self.process.udf['Courier']
        )

        subject = ', '.join(p.name for p in self.projects) + ': Container Ready For Dispatch'

        self.send_mail(subject, msg, config_name='projects-lab')


if __name__ == '__main__':
    ContainerReadyDispatch().run()
