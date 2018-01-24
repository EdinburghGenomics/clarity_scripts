import os
import platform
import pytest
from egcg_core.config import cfg
from scripts.email_data_trigger import DataReleaseEmailAndUpdateEPP
from tests.test_common import TestEPP, NamedMock
from unittest.mock import Mock, patch, PropertyMock


class TestDataReleaseEmailAndUpdateEPP(TestEPP):
    def setUp(self):
        cfg.load_config_file(os.path.join(self.etc_path, 'example_clarity_script.yml'))

        self.epp = DataReleaseEmailAndUpdateEPP(
            'http://server:8080/a_step_uri',
            'a_user',
            'a_password',
            self.log_file
        )
        project1 = NamedMock(real_name='project1')
        project2 = NamedMock(real_name='project2')

        self.patch_project_multi = patch.object(
            DataReleaseEmailAndUpdateEPP,
            'projects',
            new_callable=PropertyMock(return_value=[project1, project2])
        )
        project1 = NamedMock(real_name='project1')
        self.patch_project_single = patch.object(
            DataReleaseEmailAndUpdateEPP,
            'projects',
            new_callable=PropertyMock(return_value=[project1])
        )
        self.patch_process = patch.object(
            DataReleaseEmailAndUpdateEPP,
            'process',
            new_callable=PropertyMock(return_value=Mock(udf={
                'Data Download Contact Name 1': 'John Doe',
                'Data Download Contact Name 2': 'Jane Doe',
                'Is Contact 1 A New or Existing User?': 'New User',
                'Is Contact 2 A New or Existing User?': 'Existing User'
            }))
        )
        sample1 = NamedMock(real_name='sample1')
        sample2 = NamedMock(real_name='sample2')
        self.patch_samples = patch.object(
            DataReleaseEmailAndUpdateEPP,
            'samples',
            new_callable=PropertyMock(return_value=[sample1, sample2])
        )

        self.patch_email = patch('egcg_core.notifications.email.send_email')

    def test_send_email(self):
        with pytest.raises(ValueError):
            with self.patch_project_multi:
                self.epp._run()

        with self.patch_project_single, self.patch_process, self.patch_samples, self.patch_email as mocked_send_email:
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
            mocked_send_email.assert_called_with(
                msg=msg,
                subject='project1: Please release data',
                mailhost='smtp.test.me',
                port=25,
                sender='sender@email.com',
                recipients=['recipient1@email.com', 'recipient2@email.com'],
                strict=True
            )
