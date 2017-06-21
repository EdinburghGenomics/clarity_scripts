import os
import argparse
from urllib import parse as urlparse
from logging import FileHandler
from io import StringIO
from cached_property import cached_property
from egcg_core.config import cfg
from egcg_core.notifications import email
from genologics.lims import Lims
from genologics.entities import Process, Artifact
from egcg_core.app_logging import AppLogger, logging_default


class StepEPP(AppLogger):
    _lims = None
    _process = None

    def __init__(self, step_uri, username, password, log_file=None):
        split_url = urlparse.urlsplit(step_uri)
        self.baseuri = '%s://%s' % (split_url.scheme, split_url.netloc)
        self.username = username
        self.password = password
        self.step_id = split_url.path.split('/')[-1]
        self.open_files = []

        if log_file:
            logging_default.add_handler(FileHandler(log_file))

    @cached_property
    def lims(self):
        return Lims(self.baseuri, self.username, self.password)

    @cached_property
    def process(self):
        return Process(self.lims, id=self.step_id)

    def step(self):
        return self.process.step

    @cached_property
    def artifacts(self):
        """This is the input artifacts of that step"""
        return self.process.all_inputs(unique=True, resolve=True)

    @cached_property
    def output_artifacts(self):
        """This is the output artifacts of that step"""
        return self.process.all_outputs(unique=True, resolve=True)

    @cached_property
    def samples(self):
        """This is the samples associated with the input artifacts of that step"""
        samples = [a.samples[0] for a in self.artifacts]
        self.lims.get_batch(samples)
        return samples

    @cached_property
    def projects(self):
        """This is the projects associated with the input artifacts of that step"""
        return list(set([s.project for s in self.samples]))

    def open_or_download_file(self, file_or_uid):
        if os.path.isfile(file_or_uid):
            f = open(file_or_uid)
        else:
            a = Artifact(self.lims, id=file_or_uid)
            f = StringIO(self.lims.get_file_contents(uri=a.files[0].uri))

        self.open_files.append(f)
        return f

    def _run(self):
        raise NotImplementedError

    def run(self):
        try:
            self._run()
        except Exception as e:
            self.critical('Encountered a %s exception: %s', e.__class__.__name__, str(e))
            import traceback
            stacktrace = traceback.format_exc()
            self.error('Stack trace below:\n' + stacktrace)
            raise e

    def __del__(self):
        for f in self.open_files:
            f.close()


class SendMailEPP(StepEPP):
    @staticmethod
    def get_email_template(name='default_email_template.html'):
        return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'etc', name)

    def get_config(self, config_name=None, template_name='default_email_template.html'):
        email_config = cfg.query('email_notify', 'default')
        if config_name:
            email_config.update(cfg.query('email_notify', config_name))
        if not 'email_template' not in email_config:
            email_config['email_template'] = self.get_email_template(template_name)
        return email_config

    def send_mail(self, subject, msg, config_name=None, template_name='default_email_template.html'):
        email.send_email(msg=msg, subject=subject, strict=True, **self.get_config(config_name, template_name))

    def _run(self):
        raise NotImplementedError


def get_workflow_stage(lims, workflow_name, stage_name=None):
    workflows = [w for w in lims.get_workflows() if w.name == workflow_name]
    if len(workflows) != 1:
        return
    if not stage_name:
        return workflows[0].stages[0]
    stages = [s for s in workflows[0].stages if s.name == stage_name]
    if len(stages) != 1:
        return
    return stages[0]


def step_argparser():
    a = argparse.ArgumentParser()
    a.add_argument('-u', '--username', type=str, help='The username of the person logged in')
    a.add_argument('-p', '--password', type=str, help='The password used by the person logged in')
    a.add_argument('-s', '--step_uri', type=str, help='The uri of the step this EPP is attached to')
    a.add_argument('-l', '--log_file', type=str, help='Optional log file to append to', default=None)
    return a
