from collections import defaultdict

from EPPs.common import step_argparser, SendMailEPP
from EPPs.config import load_config


class DataReleaseEmailAndUpdateEPP(SendMailEPP):

    def _run(self):
        sample_per_project = defaultdict(list)
        for sample in self.samples:
            sample_per_project[sample.project.name].append(sample.name)
        project_list = ['%s: %s sample(s)' % (len(sample_per_project[p]), p) for p in sample_per_project]

        msg = '''Hi,

Data has just been released to the user for {number_project} project(s).
{project_list}
Please check the following link for details:
{link}

Kind regards,
Clarity X
    '''
        msg = msg.format(
            number_project=len(self.projects),
            project_list='\n'.join(project_list),
            link=self.baseuri + '/clarity/work-details/' + self.step_id[3:]
        )
        subject = ', '.join([p.name for p in self.projects]) + ': Edinburgh Genomics Clinical- Data Released'
        self.send_mail(subject, msg)


def main():
    p = step_argparser()
    args = p.parse_args()
    load_config()
    action = DataReleaseEmailAndUpdateEPP(
        args.step_uri, args.username, args.password, args.log_file,
    )
    action.run()


if __name__ == "__main__":
    main()