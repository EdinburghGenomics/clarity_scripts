#!/usr/bin/env python
import platform
from EPPs.common import step_argparser, SendMailEPP
from EPPs.config import load_config


class DataReleaseEmailAndUpdateEPP(SendMailEPP):
    def _run(self):
        if len(self.projects) > 1:
            raise ValueError('More than one project present in step. Only one project per step permitted')

        data_download_contacts = []
        # There are up to 5 contacts entered in the step.
        for count in range(1, 6):
            udf_name1 = "Data Download Contact Name %s" % count
            udf_name2 = "Is Contact %s A New or Existing User?" % count
            if self.process.udf.get(udf_name1):
                data_download_contacts.append(
                    '%s (%s)' % (self.process.udf.get(udf_name1), self.process.udf.get(udf_name2))
                )
        # Create the message
        msg = '''Hi Bioinformatics,

Please release the data for {sample_count} sample(s) from project {project} shown at the link below:

{link}

The data contacts are:

{data_download_contacts}

Kind regards,
ClarityX'''
        # fill in message with parameters
        msg = msg.format(
            link='https://'+platform.node() + '/clarity/work-details/' + self.step_id[3:],
            sample_count=len(self.samples),
            project=self.projects[0].name,
            data_download_contacts='\n'.join(data_download_contacts)
        )
        subject = ', '.join([p.name for p in self.projects]) + ': Please release data'

        # Send email to list of persons specified in the default section of config
        self.send_mail(subject, msg)


def main():
    # Get the default command line options
    p = step_argparser()
    args = p.parse_args()
    load_config()

    # Setup the EPP
    action = DataReleaseEmailAndUpdateEPP(
        args.step_uri, args.username, args.password, args.log_file,
    )

    action.run()


if __name__ == "__main__":
    main()
