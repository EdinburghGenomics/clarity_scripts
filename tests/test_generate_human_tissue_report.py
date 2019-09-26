from unittest.mock import patch
from datetime import date

from scripts.generate_human_tissue_report import GenerateHumanTissueReport
from tests.test_common import TestEPP, FakeEntitiesMaker, NamedMock


class TestGenerateHumanTissueReport(TestEPP):
    # today's date required for file name and email
    todays_date = str(date.today())
    # csv report needs to be accessible throughout object
    report_path = 'Human_Tissue_Report_' + todays_date + '.xlsx'

    #fake udfs required for LIMS get call
    project_udfs = {'REC#':'EthicNumber1', 'Organisation providing ethical consent approval':'Spectra'}
    sample_udfs1 = {'Freezer':'FREEZER1', 'Shelf':'SHELF1'}
    sample_udfs2 = {'Freezer': 'Sample Destroyed', 'Shelf': 'Sample Destroyed'}

    #wmock the return value of the function get_human_artifacts that calls lims
    mock_submitted_samples = [NamedMock(real_name='Sample1',
                                       project=NamedMock(real_name='X9999', udf=project_udfs),
                                       udf=sample_udfs1),
                              NamedMock(real_name='Sample2',
                                        project=NamedMock(real_name='X9999', udf=project_udfs),
                                        udf=sample_udfs2)
                              ]
    #patch get human artifacts, patch email send and patch saving of report
    patched_get_human_artifacts = patch('scripts.generate_human_tissue_report.get_human_artifacts', return_value=mock_submitted_samples)
    patch_email = patch('egcg_core.notifications.email.send_email')
    patch_workbook_save = patch('openpyxl.workbook.workbook.Workbook.save')

    def setUp(self):
        self.epp = GenerateHumanTissueReport(self.default_argv)

    def test_generate_report_and_send_email(self):
        fem = FakeEntitiesMaker()
        self.epp.lims = fem.lims
        with self.patched_get_human_artifacts, self.patch_email as mocked_email, self.patch_workbook_save as mocked_report_save:
            self.epp._run()

            #test that email is sent correctly
            msg= "Hi,\n\nPlease find attached the Human Tissue Report from Edinburgh Genomics Clinical for %s.\n\nKind Regards,\nEdinburgh Genomics" % self.todays_date

            mocked_email.assert_called_with(
                attachments=[self.report_path],
                msg=msg,
                subject= "Human Tissue Report - Edinburgh Genomics - " + self.todays_date,
                mailhost='smtp.test.me',
                port=25,
                sender='sender@email.com',
                recipients=['lab@email.com', 'project@email.com'],
                strict=True
            )
            #test that report is created without generating error
            mocked_report_save.assert_called_with(filename=self.report_path)

