import os
import platform
from egcg_core.config import cfg
from EPPs.common import SendMailEPP
from scripts.email_data_release import DataReleaseEmail
from scripts.email_data_trigger import DataReleaseTrigger
from scripts.email_fluidx_sample_receipt import FluidXSampleReceiptEmail
from scripts.email_receive_sample import ReceiveSampleEmail
from scripts.email_data_release_facility_manager import DataReleaseFMEmail
from tests.test_common import TestEPP, NamedMock
from unittest.mock import Mock, patch, PropertyMock


class TestEmailEPP(TestEPP):
    patch_project_multi = patch.object(
        SendMailEPP,
        'projects',
        new_callable=PropertyMock(return_value=[NamedMock(real_name='project1'), NamedMock(real_name='project2')])
    )

    patch_project_single = patch.object(
        SendMailEPP,
        'projects',
        new_callable=PropertyMock(return_value=[NamedMock(real_name='project1')])
    )

    patch_samples = patch.object(
        SendMailEPP,
        'samples',
        new_callable=PropertyMock(return_value=[NamedMock(real_name='sample1'), NamedMock(real_name='sample2')])
    )

    patch_email = patch('egcg_core.notifications.email.send_email')

    def setUp(self):
        super().setUp()
        cfg.load_config_file(os.path.join(self.etc_path, 'example_clarity_script.yml'))
        self.patch_process = self.create_patch_process(SendMailEPP)

    def test_only_one_project(self):
        try:
            with self.assertRaises(ValueError):
                with self.patch_project_multi:
                    self.epp._run()

        except NotImplementedError:
            print('Skipping test for abstract class: ' + self.epp.__class__.__name__)

    def create_epp(self, klass):
        return klass('http://server:8080/a_step_uri', 'a_user', 'a_password', self.log_file)

    @staticmethod
    def create_patch_process(klass, udfs=None):
        return patch.object(
            klass,
            'process',
            new_callable=PropertyMock(return_value=Mock(udf=udfs))
        )


class TestDataReleaseTriggerEmail(TestEmailEPP):
    def setUp(self):
        super().setUp()
        self.epp = self.create_epp(DataReleaseTrigger)
        self.patch_process = self.create_patch_process(
            DataReleaseTrigger,
            {
                'Data Download Contact Username 1': 'John Doe',
                'Data Download Contact Username 2': 'Jane Doe',
                'Is Contact 1 A New or Existing User?': 'New User',
                'Is Contact 2 A New or Existing User?': 'Existing User'
            }
        )

    def test_send_email(self):
        with self.patch_project_single, self.patch_process, self.patch_samples, self.patch_email as mocked_email:
            self.epp._run()
            msg = '''Hi Bioinformatics,

Please release the data for 2 sample(s) from project project1 shown at the link below:

https://{localmachine}/clarity/work-details/tep_uri

The data contacts are:

John Doe (New User)
Jane Doe (Existing User)

Kind regards,
ClarityX'''
            msg = msg.format(localmachine=platform.node())
            mocked_email.assert_called_with(
                msg=msg,
                subject='project1: Please release data',
                mailhost='smtp.test.me',
                port=25,
                sender='sender@email.com',
                recipients=['project@email.com', 'bfx@email.com'],
                strict=True
            )


class TestDataReleaseEmail(TestEmailEPP):
    def setUp(self):
        super().setUp()
        self.epp = self.create_epp(DataReleaseEmail)
        self.patch_process1 = self.create_patch_process(
            DataReleaseEmail,
            {'Request Customer Survey (Final Data Release)': 'No'}
        )
        self.patch_process2 = self.create_patch_process(
            DataReleaseEmail,
            {'Request Customer Survey (Final Data Release)': 'Yes'}
        )

    def test_send_email(self):
        with self.patch_project_single, self.patch_process1, self.patch_samples, self.patch_email as mocked_email:
            self.epp._run()
            msg = '''Hi,

Data for 2 sample(s) has been released for project1 at:

https://{localmachine}/clarity/work-details/tep_uri

Kind regards,
ClarityX'''
            msg = msg.format(localmachine=platform.node())

            mocked_email.assert_called_with(
                msg=msg,
                subject='project1: Data Released',
                mailhost='smtp.test.me',
                port=25,
                sender='sender@email.com',
                recipients=['finance@email.com', 'facility@email.com', 'project@email.com'],
                strict=True
            )

        with self.patch_project_single, self.patch_process2, self.patch_samples, self.patch_email as mocked_send_email:
            self.epp._run()
            # Two emails were sent
            assert mocked_send_email.call_count == 2
            msg = '''Hi,

The final data release has occurred for project1. Please request a customer survey.

Kind regards,
ClarityX'''
            # Only test the last message
            mocked_send_email.assert_called_with(
                msg=msg,
                subject='project1: Request Customer Survey - Final Data Released',
                mailhost='smtp.test.me',
                port=25,
                sender='sender@email.com',
                recipients=['finance@email.com', 'facility@email.com', 'project@email.com', 'bd@email.com'],
                strict=True
            )


class TestFluidXSampleReceiptEmail(TestEmailEPP):
    def setUp(self):
        super().setUp()
        self.epp = self.create_epp(FluidXSampleReceiptEmail)

    def test_send_email(self):
        with self.patch_project_single, self.patch_process, self.patch_samples, self.patch_email as mocked_send_email:
            self.epp._run()
            msg = '''Hi,

2 sample(s) have been received for project project1 at:

https://{localmachine}/clarity/work-details/tep_uri

Kind regards,
ClarityX'''
            msg = msg.format(localmachine=platform.node())
            # Two emails were sent
            assert mocked_send_email.call_count == 2
            mocked_send_email.assert_any_call(
                msg=msg,
                subject='project1: FluidX Tube Received',
                mailhost='smtp.test.me',
                port=25,
                sender='sender@email.com',
                recipients=['lab@email.com', 'finance@email.com', 'project@email.com'],
                strict=True
            )

            msg = '''Hi,

The manifest should now be parsed for project project1 go to the queue for step FluidX Manifest Parsing EG 1.0 ST at:

https://{localmachine}/clarity/queue/752

Kind regards,
ClarityX'''
            msg = msg.format(localmachine=platform.node())

            mocked_send_email.assert_called_with(
                msg=msg,
                subject='project1: Parse Manifest Required (FluidX)',
                mailhost='smtp.test.me',
                port=25,
                sender='sender@email.com',
                recipients=['project@email.com'],
                strict=True
            )


class TestReceiveSampleEmail(TestEmailEPP):
    def setUp(self):
        super().setUp()
        #setup epp for test email for receiving plates containing samples
        self.epp1 = ReceiveSampleEmail(
            'http://server:8080/a_step_uri',
            'a_user',
            'a_password',
            self.log_file
        )
        #set up epp for test email for receiving plates containing libraries
        self.epp2 =ReceiveSampleEmail(
            'http://server:8080/a_step_uri',
            'a_user',
            'a_password',
            self.log_file,
            upl=True
        )

    # generate test email for receiving plates containing samples
    def test_send_email_sample(self):
        with self.patch_project_single, self.patch_process, self.patch_samples, self.patch_email as mocked_email:
            self.epp1._run()
            msg = '''Hi,

2 sample(s) have been received for project1 at:

https://{localmachine}/clarity/work-details/tep_uri

Kind regards,
ClarityX'''
            msg = msg.format(localmachine=platform.node())
            mocked_email.assert_called_with(
                msg=msg,
                subject='project1: Sample Plate Received',
                mailhost='smtp.test.me',
                port=25,
                sender='sender@email.com',
                recipients=['lab@email.com', 'facility@email.com', 'finance@email.com', 'project@email.com'],
                strict=True
            )

    # generate test email for receiving plates containing libraries
    def test_send_email_library(self):
        with self.patch_project_single, self.patch_process, self.patch_samples, self.patch_email as mocked_email:
            self.epp2._run()
            msg = '''Hi,

2 libraries have been received for project1 at:

https://{localmachine}/clarity/work-details/tep_uri

Kind regards,
ClarityX'''
            msg = msg.format(localmachine=platform.node())
            mocked_email.assert_called_with(
                msg=msg,
                subject='project1: Library Plate Received',
                mailhost='smtp.test.me',
                port=25,
                sender='sender@email.com',
                recipients=['lab@email.com', 'facility@email.com', 'finance@email.com', 'project@email.com'],
                strict=True
            )

class TestDataReleaseFacilityManager(TestEmailEPP):
    def setUp(self):
        super().setUp()
        self.epp = self.create_epp(DataReleaseFMEmail)


    def test_send_email(self):
        with self.patch_project_single, self.patch_process, self.patch_samples, self.patch_email as mocked_send_email:
            self.epp._run()
            msg = '''Hi Facility Manager,

The data for 2 sample(s) is ready to be released for project1. Please can you perform the following tasks:

1) Review the list of samples at:
https://{localmachine}/clarity/work-details/tep_uri

2) Provide electronic signature

3) Click "Next Steps

Kind regards,
Clarity X'''
            msg = msg.format(localmachine=platform.node())

            mocked_send_email.assert_called_with(
                msg=msg,
                subject='project1: Review Data for Release',
                mailhost='smtp.test.me',
                port=25,
                sender='sender@email.com',
                recipients=['facility@email.com', 'project@email.com'],
                strict=True
            )