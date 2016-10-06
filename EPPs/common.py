import sys
import argparse
from logging import FileHandler
from genologics.lims import Lims
from genologics.entities import Process
from egcg_core.app_logging import AppLogger, logging_default
if sys.version_info.major == 2:
    import urlparse
else:
    from urllib import parse as urlparse


class EPP(AppLogger):
    _lims = None
    _process = None

    def __init__(self, step_uri, username, password, log_file=None):
        split_url = urlparse.urlsplit(step_uri)
        self.baseuri = '%s://%s' % (split_url.scheme, split_url.netloc)
        self.username = username
        self.password = password
        self.step_id = split_url.path.split('/')[-1]

        if log_file:
            logging_default.add_handler(FileHandler(log_file))

    @property
    def lims(self):
        if self._lims is None:
            self._lims = Lims(self.baseuri, self.username, self.password)
        return self._lims

    @property
    def process(self):
        if self._process is None:
            self._process = Process(self.lims, id=self.step_id)
        return self._process

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


def argparser():
    a = argparse.ArgumentParser()
    a.add_argument('--username', type=str, help='The username of the person logged in')
    a.add_argument('--password', type=str, help='The password used by the person logged in')
    a.add_argument('--step_uri', type=str, help='The uri of the step this EPP is attached to')
    a.add_argument('--log_file', type=str, help='Optional log file to write to', default=None)
    return a
