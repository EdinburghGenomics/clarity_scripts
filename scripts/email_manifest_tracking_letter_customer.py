#!/usr/bin/env python

from egcg_core.config import cfg

from EPPs.common import SendMailEPP


class EmailManifestLetter(SendMailEPP):
    _max_nb_projects = 1

    # populate the sample manifest with the sample date. Sample manifest template is determined by a step udf.
    # The starting row and columns are determined by step UDFs.

    _use_load_config = True  # should the config file be loaded?

    # additional argument required to obtain the file location for newly create manifest in the LIMS step
    def __init__(self, argv=None):
        super().__init__(argv)
        self.manifest = self.cmd_args.manifest
        self.letter = self.cmd_args.letter

    @staticmethod
    def add_args(argparser):
        argparser.add_argument(
            '-m', '--manifest', type=str, required=True, help='Sample manifest generated by the LIMS',
        )
        argparser.add_argument(
            '-t', '--letter', type=str, required=True, help='Sample tracking letter generated by the LIMS'
        )

    def _run(self):

        # obtain all of the inputs for the step
        all_inputs = list(self.artifacts)
        input_project_name = self.projects[0].name

        manifest_filepath = self.manifest + '-' + 'Edinburgh_Genomics_Sample_Submission_Manifest_' + input_project_name + '.xlsx'
        letter_filepath = self.letter + '-Edinburgh_Genomics_Sample_Tracking_Letter_' + self.projects[0].name + '.docx'

        # send an email to the project manager using customer manifest template with the new manifest attached

        # choose a species for the email subject, this can be updated manually by the project manager
        species = ', '.join(set(s.udf['Species'] for s in self.samples))

        email_subject = input_project_name + ": " + species + " WGS Sample Submission"

        # the manifest and relevant requirements document for the container type should be attached to the email.
        attachments_list = []
        attachments_list.append(manifest_filepath)
        # the container type influences which requirements document is attached and whether the tracking letter is attached
        container_type_name = all_inputs[0].container.type.name
        if container_type_name == '96 well plate':
            attachments_list.append(cfg.query('file_templates', 'requirements', 'plate'))
            template_name = 'customer_manifest.html'
        elif container_type_name == 'rack 96 positions':
            attachments_list.append(cfg.query('file_templates', 'requirements', 'tube'))
            template_name = 'customer_manifest.html'
        elif container_type_name == 'SGP rack 96 positions':
            attachments_list.append(letter_filepath)
            template_name = 'basic_email_template.html'

        else:
            raise ValueError('Unexpected container type name: %s' % container_type_name)

        self.send_mail(email_subject, None, project=input_project_name, template_name=template_name,
                       config_name='projects_only', attachments=attachments_list)


if __name__ == '__main__':
    EmailManifestLetter().run()
