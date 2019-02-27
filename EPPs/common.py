import argparse
import csv
import os
import sys
import argparse
from collections import defaultdict
from io import StringIO, BytesIO
from urllib import parse as urlparse
from logging import FileHandler
from urllib import parse as urlparse

import EPPs
from EPPs.config import load_config
from cached_property import cached_property
from egcg_core import rest_communication, app_logging
from egcg_core.config import cfg
from egcg_core.notifications import email
from pyclarity_lims.entities import Process, Artifact
from pyclarity_lims.lims import Lims
from requests.exceptions import ConnectionError


class InvalidStepError(Exception):
    """Exception raised when error occurred during the script due to the step being Invalid"""

    def __init__(self, message):
        super().__init__(message)
        self.message = message


class StepEPP(app_logging.AppLogger):
    _etc_path = os.path.join(os.path.dirname(os.path.abspath(EPPs.__file__)), 'etc')
    _lims = None
    _process = None
    _use_load_config = True

    # Step Validation parameters
    _max_nb_input_containers = None
    _max_nb_output_containers = None
    _max_nb_inputs = None
    _nb_analytes_per_input = None
    _nb_resfiles_per_input = None
    _max_nb_projects = None

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

    def open_or_download_file(self, file_or_uid, encoding=None, crlf=False, binary=False):
        if os.path.isfile(file_or_uid):
            if binary:
                f = open(file_or_uid, mode='rb')
            else:
                f = open(file_or_uid)
        else:
            a = Artifact(self.lims, id=file_or_uid)
            if a.files:
                if binary:
                    f = BytesIO(self.lims.get_file_contents(uri=a.files[0].uri, encoding=encoding, crlf=crlf, binary=True))
                else:
                    f = StringIO(self.lims.get_file_contents(uri=a.files[0].uri, encoding=encoding, crlf=crlf))
            else:
                f = None
        if f:
            self.open_files.append(f)
        return f

    def find_available_container(self, project, container_type=None, container_limit=99):
        """
        Check to see if a container name is available, and recurse with incremented container numbers until an available
        container name is found.
        :param str project:
        :param str container_type:
        :param int container_limit:
        """
        if container_type == '96 well plate':
            name_template = project + 'P%03d'
            container_limit = 999

        if container_type == 'rack 96 positions':
            name_template = project + 'R%02d'
            container_limit = 99

        for container_count in range(1, container_limit + 1):
            new_name = name_template % container_count
            if not self.lims.get_containers(name=new_name):
                return new_name
        raise ValueError('Cannot allocate more than %s containers of type %s ' % (container_limit, container_type))

    def _run(self):
        raise NotImplementedError

    def run(self):
        try:
            self._validate_step()
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

    @cached_property
    def input_container_names(self):
        """The name of containers from input artifacts. """
        containers = set()
        for art in self.artifacts:
            # Check to see if artifact has a container before retrieving the container.
            # Artifacts that are not samples will not have containers.
            if art.container:
                containers.add(art.container.name)
        return sorted(containers)

    @cached_property
    def output_container_names(self):
        """The name of containers from output artifacts"""
        containers = set()
        for art in self.output_artifacts:
            # Check to see if artifact has a container before retrieving the container.
            # Artifacts that are not samples will not have containers.
            if art.container:
                containers.add(art.container.name)
        return sorted(containers)

    def _validate_step(self):
        """Perform the Step EPP's validations when required.
        All validations are optionals and will require sub classes to set the corresponding varaibles:

         - _max_nb_input_containers: set the maximum number of input container of the step.
         - _max_nb_output_containers: set the maximum number of output container of the step.
         - _max_nb_input: set the maximum number of input of the step.
         - _nb_analyte_per_input: set the number of replicates (Analytes) required for the step.
         - _nb_resfile_per_input: set the number of replicates (ResultFiles) required for the step.
         - _max_nb_project: set the maximum number of project in the step.
        """
        if self._max_nb_input_containers is not None:
            # check the number of input containers
            if len(self.input_container_names) > self._max_nb_input_containers:
                raise InvalidStepError(
                    'Maximum number of input container is %s. There are %s input container in the step.' % (
                        self._max_nb_input_containers, len(self.input_container_names)
                    )
                )
        if self._max_nb_output_containers is not None:
            # check the number of output containers
            if len(self.output_container_names) > self._max_nb_output_containers:
                raise InvalidStepError(
                    'Maximum number of output plates is %s. There are %s output plates in the step.' % (
                        self._max_nb_output_containers, len(self.output_container_names)
                    )
                )
        if self._max_nb_inputs is not None:
            if len(self.artifacts) > self._max_nb_inputs:
                raise InvalidStepError(
                    "Maximum number of inputs is %s. %s inputs present in step." % (
                        self._max_nb_inputs, len(self.artifacts)
                    )
                )
        if self._nb_analytes_per_input is not None:
            for artifact in self.artifacts:
                outputs = self.process.outputs_per_input(artifact.id, Analyte=True)
                if len(outputs) != self._nb_analytes_per_input:
                    raise InvalidStepError(
                        "%s replicates required for each input. "
                                "%s replicates found for %s." % (self._nb_analytes_per_input, len(outputs), artifact.id)
                    )
        if self._nb_resfiles_per_input is not None:
            for artifact in self.artifacts:
                outputs = self.process.outputs_per_input(artifact.id, ResultFile=True)
                if len(outputs) != self._nb_resfiles_per_input:
                    raise InvalidStepError(
                        "%s replicates required for each input. "
                                "%s replicates found for %s." % (self._nb_analytes_per_input, len(outputs), artifact.id)
                    )
        if self._max_nb_projects is not None:
            if len(self.projects) > self._max_nb_projects:
                raise InvalidStepError(
                    'Maximum number of projet in step is %s. %s projects found.' % (
                        self._max_nb_projects, len(self.projects)
                    )
                )

    def __del__(self):
        if hasattr(self,'open_files'):
            for f in self.open_files:
                f.close()


class SendMailEPP(StepEPP):
    def get_email_template(self, name=None):
        return os.path.join(self._etc_path, name)

    def get_config(self, config_heading_1=None, config_heading_2=None, config_heading_3=None, template_name=None):
        if config_heading_1==None or config_heading_1== 'email_notify':
            if config_heading_2:
                config = cfg.query('email_notify', 'default')
                config.update(cfg.query('email_notify', config_heading_2))
            elif not config_heading_2:
                config = cfg.query(config_heading_1, 'default')
            if 'email_template' not in config and template_name:
                config['email_template'] = self.get_email_template(template_name)
        if config_heading_1== 'file_templates':
            if config_heading_3:
                config = cfg.query(config_heading_1,config_heading_2,config_heading_3)
            else:
                config = cfg.query(config_heading_1, config_heading_2)

        return config

    def send_mail(self, subject, msg, config_name=None, template_name=None, attachments=None, **kwargs):
        tmp_dict = {}
        tmp_dict.update(self.get_config(config_heading_2=config_name, template_name=template_name))
        tmp_dict.update(kwargs)
        email.send_email(msg=msg, subject=subject, strict=True,attachments=attachments,**tmp_dict)

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

    def __init__(self, argv=None):
        """ additional argument required for the location of the Hamilton input file so def __init__ customised."""
        super().__init__(argv)
        self.hamilton_input = self.cmd_args.hamilton_input
        self.shared_drive_path = os.path.abspath(self.cmd_args.shared_drive_path)

        assert self.csv_column_headers is not None, 'csv_column_headers needs to be set by the child class'
        assert self.output_file_name is not None, 'output_file_name needs to be set by the child class'
        assert self._max_nb_input_containers is not None, 'number of permitted input containers needs to be set ' \
                                                          'by the child class'
        assert self._max_nb_output_containers is not None, 'number of permitted output containers needs to be set ' \
                                                           'by the child class'

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
        with open(filename, 'w', newline='') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerows(csv_array)

    @cached_property
    def input_container_names(self):
        """The name of containers from input artifacts.
        Disregards standards containers as these are not stored correctly in the LIMS.
        Standards are identified as the sample well location is 1:1"""
        containers = set()

        for art in self.artifacts:
            # Check to see if artifact has a container before retrieving the container.
            # Artifacts that are not samples will not have containers.
            if art.container and art.location[1] != '1:1':
                containers.add(art.container.name)
        return sorted(containers)

    @property
    def shared_drive_file_path(self):
        return os.path.join(self.shared_drive_path, self.output_file_name)

    def _generate_csv_dict(self):
        """Provides the lines to write to the csv files in a dictionary
        where the key is a well position such as 'A:1' and the value is the line of the csv. """
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

        counter = 0
        for column in self.plate_columns:
            for row in self.plate_rows:
                if row + ":" + column in csv_dict.keys():
                    csv_rows.append(csv_dict[row + ":" + column])
                    counter += 1

        if counter == 0:
            raise InvalidStepError("No valid keys present in csv_dict. Key format must be row:column e.g. A:1.")

        return csv_rows

    def _run(self):
        """Generic run that check the number of input and output container
        then creates the two csv files ('-hamilton_input.csv' and the one on the shared drive)."""
        csv_array = self.generate_csv_array()
        # Create and write the Hamilton input file, this must have the hamilton_input argument as the prefix as
        # this is used by Clarity LIMS to recognise the file and attach it to the step
        self.write_csv(self.hamilton_input + '-hamilton_input.csv', csv_array)
        self.write_csv(self.shared_drive_file_path, csv_array)


class ParseSpectramaxEPP(StepEPP):
    _use_load_config = False  # prevent the loading of the config
    # define the starting well for data parsing e.g. if the standards occupy the first 24 wells, parsing should start from well A4. No semi-colon
    # separate row and column
    starting_well = None

    def __init__(self, argv=None):
        """ additional argument required for the location of the Hamilton input file so def __init__ customised."""
        super().__init__(argv)
        self.spectramax_file = self.cmd_args.spectramax_file
        self.sample_concs = {}
        self.plate_names = []
        self.plates = defaultdict(dict)

        assert self.starting_well is not None, 'starting_well needs to be set by the child class'

    @staticmethod
    def add_args(argparser):
        argparser.add_argument('--spectramax_file', type=str, required=True,
                               help='Spectramax output file from the step')

    def parse_spectramax_file(self):
        f = self.open_or_download_file(self.spectramax_file, encoding='utf-16', crlf=True)
        encountered_unknowns = False
        in_unknowns = False

        for line in f:
            if line.startswith('Group: Unknowns'):
                assert not in_unknowns
                in_unknowns = True
                encountered_unknowns = True

            elif line.startswith('~End'):
                in_unknowns = False

            elif in_unknowns:
                if line.startswith('Sample') or line.startswith('Group Summaries'):
                    pass
                else:

                    split_line = line.split('\t')
                    self.sample_concs[int(split_line[0])] = (split_line[1], float(split_line[3]))

            elif line.startswith('Plate:') and encountered_unknowns:
                self.plate_names.append(line.split('\t')[1])

        if self.sample_concs[1][0] != self.starting_well:
            raise AssertionError(
                'Badly formed spectramax file: first well for samples is %s but expected to be %s'
                % (str(self.sample_concs[1][0]),str(self.starting_well))
            )

        self.debug('Found %s samples and %s plates', len(self.sample_concs), len(self.plate_names))

    def assign_samples_to_plates(self):

        plate_idx = -1
        plate_name = None
        for i in sorted(self.sample_concs):  # go through in ascending order...
            coord, conc = self.sample_concs[i]
            if coord == self.starting_well:  # ... and take the variable starting_well coord as the start of a new plate
                plate_idx += 1
                plate_name = self.plate_names[plate_idx]

            if coord in self.plates[plate_name]:
                raise AssertionError(
                    'Badly formed spectramax file: tried to add coord %s for sample %s to plate %s' % (
                        coord, i, plate_name
                    )
                )
            self.plates[plate_name][coord] = conc

    def _add_plates_to_step(self):
        # populates the artifacts with the data from result file based on plate and well position. Data uploaded to LIMS with put batch
        raise NotImplementedError

    def _run(self):

        self.parse_spectramax_file()
        self.assign_samples_to_plates()
        batch_artifacts = self._add_plates_to_step()

        self.lims.put_batch(list(batch_artifacts))


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
