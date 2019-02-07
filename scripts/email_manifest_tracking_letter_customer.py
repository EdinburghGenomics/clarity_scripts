#!/usr/bin/env python
import itertools
from openpyxl import load_workbook
import os

from EPPs.common import SendMailEPP


class EmailManifestLetter(SendMailEPP):
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
        all_inputs = self.process.artifacts
        input_project_name=self.projects[0].name


        # create list of unique containers
        container_types = set()
        unique_container_names=set()


        for artifact in all_inputs:
            container_types.add(artifact.container.type.name)
            unique_container_names.add(artifact.container.name)


        manifest_filepath=self.manifest + '-'+'Edinburgh_Genomics_Sample_Submission_Manifest_' + input_project_name + '.xlsx'
        letter_filepath=self.letter+'-Edinburgh_Genomics_Sample_Tracking_Letter_'+all_inputs[0].samples[0].project.name+'.docx'

        #send an email to the project manager using customer manifest template with the new manifest attached

        #choose a species for the email subject, this can be updated manually by the project manager
        species=all_inputs[0].samples[0].udf['Species']
        email_subject= input_project_name+": "+species+" WGS Sample Submission"

        #the manifest and relevant requirements document for the container type should be attached to the email.
        attachments_list=[]
        attachments_list.append(manifest_filepath)
        #the container type influences which requirements document is attached and whether the tracking letter is attached
        container_type_name=all_inputs[0].container.type.name
        if container_type_name=='96 well plate':
            attachments_list.append(self.get_config(config_heading_1='file_templates',config_heading_2='requirements',config_heading_3='plate'))
            template_name = 'customer_manifest.html'
        elif container_type_name=='rack 96 positions':
            attachments_list.append(self.get_config(config_heading_1='file_templates',config_heading_2='requirements',config_heading_3='tube'))
            attachments_list.append(letter_filepath)
            template_name = 'customer_manifest.html'
        elif container_type_name=='SGP rack 96 positions':
            attachments_list.append(letter_filepath)
            template_name = 'basic_email_template.html'

        self.send_mail(email_subject,None, project=input_project_name,template_name=template_name,
                       config_name='projects_only', attachments=attachments_list)


if __name__ == '__main__':
    EmailManifestLetter().run()
