import csv
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


class InvalidStepError(BaseException):
    """Exception raised when error occured during the script due to the step being Invalid"""
    def __init__(self, message):
        self.message = message


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

    def _run(self):
        raise NotImplementedError

    def run(self):
        try:
            return self._run()
        except InvalidStepError as e:
            print(e.message)
            sys.exit(1)
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


class GenerateHamiltonInputEPP(StepEPP):

    # define the rows and columns in the input plate (standard 96 well plate pattern)
    plate_rows = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
    plate_columns = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
    csv_column_headers = None
    output_file_name = None
    permitted_input_containers = None
    permitted_output_containers = None

    def __init__(self, argv=None):
        """ additional argument required for the location of the Hamilton input file so def __init__ customised."""
        super().__init__(argv)
        self.hamilton_input = self.cmd_args.hamilton_input
        self.shared_drive_path = os.path.abspath(self.cmd_args.shared_drive_path)

        assert self.csv_column_headers is not None, 'csv_column_headers needs to be set by the child class'
        assert self.output_file_name is not None, 'output_file_name needs to be set by the child class'
        assert self.permitted_input_containers is not None, 'number of permitted input containers needs to be set by the child class'
        assert self.permitted_output_containers is not None, 'number of permitted output containers needs to be set by the child class'


    @staticmethod
    def add_args(argparser):
        argparser.add_argument(
            '-i', '--hamilton_input', type=str, required=True, help='Hamilton input file generated by the LIMS'
        )
        argparser.add_argument(
            '-d', '--shared_drive_path', type=str, required=True,
            help='Shared drive path location for Hamilton input file'
        )

    @staticmethod
    def write_csv(filename, csv_array):
        """Write the list of list to the file provided as a csv file"""
        with open(filename, 'w') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerows(csv_array)

    @cached_property
    def input_container_names(self):
        """The name of containers from input artifacts. Disregards stanards containers as these are not stored correctly
        in the LIMS. Standards are identified as the sample well location is 1:1"""
        containers = []

        for art in self.artifacts:
            if art.type == 'Analyte' and art.container and art.location[1] != '1:1':
                containers.append(art.container.name)
        return list(frozenset(containers))

    @cached_property
    def output_container_names(self):
        """The name of containers from output artifacts"""
        containers = []
        for art in self.output_artifacts:
            if art.type == 'Analyte' and art.container:
                containers.append(art.container.name)
        return list(frozenset(containers))

    @property
    def shared_drive_file_path(self):
        return os.path.join(self.shared_drive_path, self.output_file_name)

    def _generate_csv_dict(self):
        """Provides the lines to write to the csv files in a dictionary
        where the key is a well position such as a  """
        raise NotImplementedError

    def generate_csv_array(self):
        """
        Generate the csv array from the implemented csv dictionary.
        It sorts the csv lines by column (self.plate_columns) then row (self.plate_rows)
        """
        csv_dict = self._generate_csv_dict()

        if self.csv_column_headers:
            csv_rows = [self.csv_column_headers]
        else:
            csv_rows = []
        for column in self.plate_columns:
            for row in self.plate_rows:
                if row + ":" + column in csv_dict.keys():
                    csv_rows.append(csv_dict[row + ":" + column])
        return csv_rows

    def _run(self):
        """Generic run that make a check of unique input container and unique output container
        then creates the two csv files ('-hamilton_input.csv' and the one on the shared drive)."""
        # check the number of input containers
        if len(self.input_container_names) > self.permitted_input_containers:
            raise InvalidStepError(message='Maximum number of input plates is %s. There are %s input plates in the step.' % (self.permitted_input_containers,len(self.input_container_names)))
        # check the number of output containers
        if len(self.output_container_names) > self.permitted_output_containers:
            raise InvalidStepError(message='Maximum number of output plates is %s. There are %s output plates in the step.' % (self.permitted_output_containers,len(self.output_container_names)))
        csv_array = self.generate_csv_array()
        # Create and write the Hamilton input file, this must have the hamilton_input argument as the prefix as
        # this is used by Clarity LIMS to recognise the file and attach it to the step
        self.write_csv(self.hamilton_input + '-hamilton_input.csv', csv_array)
        self.write_csv(self.shared_drive_file_path, csv_array)


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
