import os
import sys
import argparse
from io import StringIO
from urllib import parse as urlparse
from logging import FileHandler
from cached_property import cached_property
from requests.exceptions import ConnectionError
from pyclarity_lims.lims import Lims
from pyclarity_lims.entities import Process, Artifact
from egcg_core import rest_communication, app_logging
from egcg_core.config import cfg
from egcg_core.notifications import email
import EPPs
from EPPs.config import load_config


class StepEPP(app_logging.AppLogger):
    _etc_path = os.path.join(os.path.dirname(os.path.abspath(EPPs.__file__)), 'etc')
    _lims = None
    _process = None
    _use_load_config = True

    def __init__(self, argv=None):
        self.argv = argv
        args = self.cmd_args

        split_url = urlparse.urlsplit(args.step_uri)
        self.baseuri = '%s://%s' % (split_url.scheme, split_url.netloc)
        self.username = args.username
        self.password = args.password
        self.step_id = split_url.path.split('/')[-1]
        self.open_files = []

        if args.log_file:
            app_logging.logging_default.add_handler(FileHandler(args.log_file))

        if self._use_load_config:
            load_config()

    @cached_property
    def cmd_args(self):
        a = argparse.ArgumentParser()
        a.add_argument('-u', '--username', type=str, help='The username of the person logged in')
        a.add_argument('-p', '--password', type=str, help='The password used by the person logged in')
        a.add_argument('-s', '--step_uri', type=str, help='The URI of the step this EPP is attached to')
        a.add_argument('-l', '--log_file', type=str, help='Optional log file to append to', default=None)
        self.add_args(a)
        return a.parse_args(self.argv)

    @staticmethod
    def add_args(argparser):
        """
        :param argparse.ArgumentParser argparser:
        """
        pass

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

    def open_or_download_file(self, file_or_uid, encoding=None, crlf=False):
        if os.path.isfile(file_or_uid):
            f = open(file_or_uid)
        else:
            a = Artifact(self.lims, id=file_or_uid)
            if a.files:
                f = StringIO(self.get_file_contents(uri=a.files[0].uri, encoding=encoding, crlf=crlf))
            else:
                f = None
        if f:
            self.open_files.append(f)
        return f

    # TODO: remove this when we switch to pyclarity_lims
    def get_file_contents(self, id=None, uri=None, encoding=None, crlf=False):
        """Returns the contents of the file of <ID> or <uri>"""
        if id:
            url = self.lims.get_uri('files', id, 'download')
        elif uri:
            url = uri.rstrip('/') + '/download'
        else:
            raise ValueError('id or uri required')

        r = self.lims.request_session.get(url, auth=(self.username, self.password), timeout=16)
        self.lims.validate_response(r)
        if encoding:
            r.encoding = encoding

        return r.text.replace('\r\n', '\n') if crlf else r.text

    def find_available_container(self, project, container_type, count=1):
        """
        Check to see if a container name is available, and recurse with incremented container numbers until an available
        container name is found.
        :param str project:
        :param int count:
        """

        if container_type=='96 well plate':
            new_name = project + 'P%03d' % count
            container_limit=999

        if container_type=='Tube':
            new_name = project+ 'R%02d' % count
            container_limit=99

        if count > container_limit:
            raise ValueError('Cannot allocate more than %s containers' % container_limit)

        if not self.lims.get_artifacts(containername=new_name):
            return new_name
        else:
            return self.find_available_container(project, container_type, count=count + 1)

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
    def get_email_template(self, name=None):
        return os.path.join(self._etc_path, name)

    def get_config(self, config_name=None, template_name=None):
        email_config = cfg.query('email_notify', 'default')
        if config_name:
            email_config.update(cfg.query('email_notify', config_name))
        if 'email_template' not in email_config and template_name:
            email_config['email_template'] = self.get_email_template(template_name)
        return email_config

    def send_mail(self, subject, msg, config_name=None, template_name=None):
        email.send_email(msg=msg, subject=subject, strict=True, **self.get_config(config_name, template_name))

    def _run(self):
        raise NotImplementedError


class RestCommunicationEPP:
    @staticmethod
    def _rest_interaction(func, *args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ConnectionError as ce:
            print('%s: %s' % (ce.__class__.__name__, ce))
            sys.exit(127)

    @classmethod
    def get_documents(cls, *args, **kwargs):
        return cls._rest_interaction(rest_communication.get_documents, *args, **kwargs)

    @classmethod
    def patch_entry(cls, *args, **kwargs):
        return cls._rest_interaction(rest_communication.patch_entry, *args, **kwargs)


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


def find_newest_artifact_originating_from(lims, process_type, sample_name):
    """
    This function retrieve the newest artifact (Analyte) associated with the provided sample name
    and originating from the provided process_type
    :param lims: The instance of the lims object
    :param process_type: the type of process that created the artifact
    :param sample_name: the name of the sample associated with this artifact.
    """
    def get_parent_process_id(art):
        return art.parent_process.id

    artifacts = lims.get_artifacts(
        process_type=process_type,
        sample_name=sample_name,
        type='Analyte'
    )
    if len(artifacts) > 1:
        # its possible that the process has occurred more than once
        # so must find the most recent occurrence of that step
        artifacts.sort(key=get_parent_process_id, reverse=True)
        # sorts the artifacts returned to place the most recent artifact at position 0 in list

    if artifacts:
        return artifacts[0]
