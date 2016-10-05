import os
import sys
import argparse
import time
from logging import FileHandler
from xml.etree import ElementTree
from genologics.entities import ReagentLot
from genologics.lims import Lims
from egcg_core.app_logging import logging_default as log_cfg
if sys.version_info.major == 2:
    import urlparse
else:
    from urllib import parse as urlparse

reagent_kit_map = {
    'PDR': 'Patterned Denaturation Reagent',
    'PRM': 'Patterned Resynthesis Mix',
    'PLM2': 'Patterned Linearization Mix 2',
    'PSM': 'Patterned Scan Mix',
    'PPM': 'Patterned Amplification Premix',
    'PAM': 'Patterned Amplification Mix',
    'PB1': 'Patterned SBS Buffer 1',
    'HP11': 'Read 2 Primer Mix',
    'PB2': 'Patterned SBS Buffer 2',
    'PIM': 'Patterned Incorporation Mix',
    'PCM': 'Patterned Cleavage Mix'
}

run_path = ''

logger = log_cfg.get_logger(__name__)


def find_run_parameters(run_name):
    if os.path.exists(os.path.join(run_path, run_name)):
        return os.path.join(run_path, run_name, 'run_parameters.xml')


def get_reagent_name_from_run_parameter(run_parameters):
    root = ElementTree.parse(run_parameters).getroot()
    for reagent in root.find('Setup/LimsReagents').getchildren():
        name = reagent.find('ReagentName').text
        lot = reagent.find('ReagentBarcode').text
        yield (name, lot)


def create_reagent_for_run(lims, run_name):
    run_parameters = find_run_parameters(run_name)
    for name, lot in get_reagent_name_from_run_parameter(run_parameters):
        reagent_lots = lims.get_reagent_lots(number=lot)
        if len(reagent_lots) == 1:
            reagent_lot = reagent_lots[0]
            if reagent_lot.status != 'active':
                reagent_lot.status = 'active'
                reagent_lot.expiry_date = time.strftime('%Y-%m,-%d')
                reagent_lot.put()
        else:
            reagent_kits = lims.get_reagent_kits(name=reagent_kit_map[name])
            if len(reagent_kits) != 1:
                raise Exception('Found %s reagent kits for name %s' % (len(reagent_kits), reagent_kit_map[name]))
            reagent_lot = ReagentLot.create(lims, reagent_kit=reagent_kits[0], name=name, lot_number=lot, expiry_date=time.strftime('%Y-%m,-%d'), status='active')

        print('Create reagent %s: %s' % (name, lot))


def main():
    args = _parse_args()
    r1 = urlparse.urlsplit(args.step_uri)
    server_http = '%s://%s' % (r1.scheme, r1.netloc)

    # Assume the step_uri contains the step id at the end
    step_id = r1.path.split('/')[-1]
    lims = Lims(server_http, args.username, args.password)

    log_cfg.add_handler(FileHandler(args.log_file))
    return create_reagent_for_run(lims, run_name)


def _parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--username', dest="username", type=str, required=True, help='The username of the person logged in')
    p.add_argument('--password', dest="password", type=str, required=True, help='The password used by the person logged in')
    p.add_argument('--step_uri', dest='step_uri', type=str, required=True, help='The uri of the step this EPP is attached to')
    p.add_argument('--log_file', dest='log_file', type=str, required=True, help='The log file containing statement about what was done')
    return p.parse_args()


if __name__ == '__main__':
    sys.exit(main())
