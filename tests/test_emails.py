import os
import platform
from unittest.mock import Mock, patch, PropertyMock

from EPPs.common import SendMailEPP
from scripts.email_container_dispatched import ContainerDispatchComplete
from scripts.email_container_ready_for_dispatch import ContainerReadyDispatch
from scripts.email_data_release import DataReleaseEmail
from scripts.email_data_release_facility_manager import DataReleaseFMEmail
from scripts.email_data_trigger import DataReleaseTrigger
from scripts.email_fluidx_sample_receipt import FluidXSampleReceiptEmail
from scripts.email_manifest_tracking_letter_customer import EmailManifestLetter
from scripts.email_receive_sample import ReceiveSampleEmail
from scripts.email_sample_disposal_notification import SampleDisposalNotificationEmail
from scripts.email_sample_disposal_review import SampleDisposalFMEmail
from tests.test_common import TestEPP, NamedMock


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
        new_callable=PropertyMock(return_value=[NamedMock(real_name='sample1', udf={'Species': 'Homo sapiens'}),
                                                NamedMock(real_name='sample2')])
    )

    patch_email = patch('egcg_core.notifications.email.send_email')

    def setUp(self):
        super().setUp()
        self.patch_process = self.create_patch_process(SendMailEPP)

    def create_epp(self, klass):
        return klass(self.default_argv)

    def manifest_epp(self, klass):
        argv = self.default_argv + [
            '--manifest', 'a_manifest',
            '--letter', 'a_letter',
        ]
        return klass(argv)

    @staticmethod
    def create_patch_process(klass, udfs=None, all_inputs=None):
        return patch.object(
            klass,
            'process',
            new_callable=PropertyMock(return_value=Mock(udf=udfs, all_inputs=all_inputs))
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
                attachments=None,
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
                attachments=None,
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
                attachments=None,
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
                attachments=None,
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
                attachments=None,
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
        # setup epp for test email for receiving plates containing samples
        self.epp1 = ReceiveSampleEmail(self.default_argv)
        # set up epp for test email for receiving plates containing libraries
        self.epp2 = ReceiveSampleEmail(self.default_argv + ['--upl'])

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
                attachments=None,
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
                attachments=None,
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
                attachments=None,
                msg=msg,
                subject='project1: Review Data for Release',
                mailhost='smtp.test.me',
                port=25,
                sender='sender@email.com',
                recipients=['facility@email.com', 'project@email.com'],
                strict=True
            )


class TestSampleDisposalFacilityManager(TestEmailEPP):
    def setUp(self):
        super().setUp()
        self.epp = self.create_epp(SampleDisposalFMEmail)

    def test_only_one_project(self):
        pass

    def test_send_email(self):
        with self.patch_project_single, self.patch_process, self.patch_samples, self.patch_email as mocked_send_email:
            self.epp._run()
            msg = '''Hi Facility Manager,

Samples are ready for disposal. Please follow the link below and perform the following tasks:

1) Review the list of samples at:
https://{localmachine}/clarity/work-details/tep_uri

2) Provide electronic signature

3) Click "Next Steps

Kind regards,
Clarity X'''
            msg = msg.format(localmachine=platform.node())

            mocked_send_email.assert_called_with(
                attachments=None,
                msg=msg,
                subject='Review Samples for Disposal',
                mailhost='smtp.test.me',
                port=25,
                sender='sender@email.com',
                recipients=['facility@email.com', 'project@email.com'],
                strict=True
            )


class TestSampleDisposalNotification(TestEmailEPP):
    def setUp(self):
        super().setUp()
        self.epp = self.create_epp(SampleDisposalNotificationEmail)

    def test_only_one_project(self):
        pass

    def test_send_email(self):
        with self.patch_project_single, self.patch_process, self.patch_samples, self.patch_email as mocked_send_email:
            self.epp._run()
            msg = '''Hi,

The samples at the link below have been approved for disposal by the Facility Manager:

https://{localmachine}/clarity/work-details/tep_uri

Kind regards,
Clarity X'''
            msg = msg.format(localmachine=platform.node())

            mocked_send_email.assert_called_with(
                attachments=None,
                msg=msg,
                subject='Samples Approved For Disposal',
                mailhost='smtp.test.me',
                port=25,
                sender='sender@email.com',
                recipients=['lab@email.com', 'project@email.com'],
                strict=True
            )


class TestEmailContainerDispatched(TestEmailEPP):
    def setUp(self):
        super().setUp()
        self.epp = self.create_epp(ContainerDispatchComplete)

    def test_send_email(self):
        with self.patch_project_single, self.patch_process, self.patch_samples, self.patch_email as mocked_send_email:
            self.epp._run()
            msg = '''Hi,

The container dispatch has been completed for project1.

https://{localmachine}/clarity/work-details/tep_uri

Kind regards,
ClarityX'''
            msg = msg.format(localmachine=platform.node())

            mocked_send_email.assert_called_with(
                attachments=None,
                msg=msg,
                subject='project1: Container Dispatched',
                mailhost='smtp.test.me',
                port=25,
                sender='sender@email.com',
                recipients=['lab@email.com', 'project@email.com'],
                strict=True
            )


class TestEmailContainerReadyDispatch(TestEmailEPP):
    def setUp(self):
        super().setUp()
        self.epp = self.create_epp(ContainerReadyDispatch)
        self.patch_process1 = self.create_patch_process(
            ContainerReadyDispatch,
            {'Courier': 'Acourier'}
        )

    def test_send_email(self):
        with self.patch_project_single, self.patch_process1, self.patch_samples, self.patch_email as mocked_send_email:
            self.epp._run()

            msg = '''Hi,

A container is ready for dispatch for project1.

Courier: Acourier

Please check the Container Shipment Preparation queue.

https://{localmachine}/clarity/

Kind regards,
ClarityX'''
            msg = msg.format(localmachine=platform.node())

            mocked_send_email.assert_called_with(
                attachments=None,
                msg=msg,
                subject='project1: Container Ready For Dispatch',
                mailhost='smtp.test.me',
                port=25,
                sender='sender@email.com',
                recipients=['lab@email.com', 'project@email.com'],
                strict=True

            )


class TestEmailManifestTrackingLetter(TestEmailEPP):
    def setUp(self):
        super().setUp()
        self.epp = self.manifest_epp(EmailManifestLetter)
        self.patch_process1 = self.create_patch_process(
            EmailManifestLetter,
            all_inputs=Mock(return_value=[
                Mock(samples=[Mock(project=NamedMock(real_name='Project1'), udf={'Species': 'Homo sapiens'})],
                     container=Mock(type=NamedMock(real_name='96 well plate')))])
        )

        self.patch_process2 = self.create_patch_process(
            EmailManifestLetter,
            all_inputs=Mock(return_value=[
                Mock(samples=[Mock(project=NamedMock(real_name='Project1'), udf={'Species': 'Homo sapiens'})],
                     container=Mock(type=NamedMock(real_name='rack 96 positions')))])
        )

        self.patch_process3 = self.create_patch_process(
            EmailManifestLetter,
            all_inputs=Mock(return_value=[
                Mock(samples=[Mock(project=NamedMock(real_name='Project1'), udf={'Species': 'Homo sapiens'})],
                     container=Mock(type=NamedMock(real_name='SGP rack 96 positions')))])
        )

        self.patch_process4 = self.create_patch_process(
            EmailManifestLetter,
            all_inputs=Mock(return_value=[
                Mock(samples=[Mock(project=NamedMock(real_name='Project1'), udf={'Species': 'Homo sapiens'})],
                     container=Mock(type=NamedMock(real_name=None)))])
        )

    def test_send_email(self):
        with self.patch_project_single, self.patch_process1, \
             self.patch_email as mocked_send_email:
            self.epp._run()
            mocked_send_email.assert_called_with(
                attachments=['a_manifest-Edinburgh_Genomics_Sample_Submission_Manifest_project1.xlsx',
                             'plate requirements'],
                msg=None,
                subject='project1: Homo sapiens WGS Sample Submission',
                mailhost='smtp.test.me',
                project='project1',
                port=25,
                sender='sender@email.com',
                recipients=['project@email.com'],
                email_template=os.path.join(self.etc_path, 'customer_manifest.html'),
                strict=True
            )

    def test_send_email2(self):
        with self.patch_project_single, self.patch_process2, \
             self.patch_email as mocked_send_email:
            self.epp._run()
            mocked_send_email.assert_called_with(
                attachments=['a_manifest-Edinburgh_Genomics_Sample_Submission_Manifest_project1.xlsx',
                             'tube requirements', 'a_letter-Edinburgh_Genomics_Sample_Tracking_Letter_project1.docx'],
                msg=None,
                subject='project1: Homo sapiens WGS Sample Submission',
                mailhost='smtp.test.me',
                project='project1',
                port=25,
                sender='sender@email.com',
                recipients=['project@email.com'],
                email_template=os.path.join(self.etc_path, 'customer_manifest.html'),
                strict=True
            )

    def test_send_email3(self):
        with self.patch_project_single, self.patch_process3, \
             self.patch_email as mocked_send_email:
            self.epp._run()
            mocked_send_email.assert_called_with(
                attachments=['a_manifest-Edinburgh_Genomics_Sample_Submission_Manifest_project1.xlsx',
                             'a_letter-Edinburgh_Genomics_Sample_Tracking_Letter_project1.docx'],
                msg=None,
                subject='project1: Homo sapiens WGS Sample Submission',
                mailhost='smtp.test.me',
                project='project1',
                port=25,
                sender='sender@email.com',
                recipients=['project@email.com'],
                email_template=os.path.join(self.etc_path, 'basic_email_template.html'),
                strict=True
            )

    def test_send_email4(self):
        with self.patch_project_single, self.patch_process4:
            with self.assertRaises(ValueError):
                self.epp._run()
