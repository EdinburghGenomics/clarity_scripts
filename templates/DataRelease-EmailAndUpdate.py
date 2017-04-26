from collections import defaultdict

from EPPs.common import step_argparser, SendMailEPP
from EPPs.config import load_config


class DataReleaseEmailAndUpdateEPP(SendMailEPP):

    def _run(self):
        # Get the number of sample per projects
        sample_per_project = defaultdict(list)
        for sample in self.samples:
            sample_per_project[sample.project.name].append(sample.name)

        # Create a list of project description like <project name>: <number of sample> sample(s)
        project_list = ['%s: %s sample(s)' % (len(sample_per_project[p]), p) for p in sample_per_project]

        # Create the message
        msg = '''Hi,

Data has just been released to the user for {number_project} project(s).
{project_list}
Please check the following link for details:
{link}

Kind regards,
Clarity X
    '''
        # fill in message with parameters
        msg = msg.format(
            number_project=len(self.projects),
            project_list='\n'.join(project_list),
            link=self.baseuri + '/clarity/work-details/' + self.step_id[3:]
        )
        subject = ', '.join([p.name for p in self.projects]) + ': Edinburgh Genomics Clinical- Data Released'

        # Send email to list of persons specified in the default section of config
        self.send_mail(subject, msg)

        # Alternatively You can send the email to specific section of config
        self.send_mail(subject, msg, config_name='project_only')


def main():
    # Ge the default command line options
    p = step_argparser()

    # Parse command line options
    args = p.parse_args()

    # Load the config from the default location
    load_config()

    # Setup the EPP
    action = DataReleaseEmailAndUpdateEPP(
        args.step_uri, args.username, args.password, args.log_file,
    )

    # Run the EPP
    action.run()


if __name__ == "__main__":
    main()