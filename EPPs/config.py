import os
from egcg_core.config import cfg


def load_config():
    cfg.load_config_file(
        os.getenv('CLARITYSCRIPTCONFIG'),
        os.path.expanduser('~/.clarity_script.yaml'),
        env_var='CLARITYSCRIPTENV'
    )
