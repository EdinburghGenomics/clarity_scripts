import argparse
import logging
import sys
import os
from xml.etree import ElementTree

import datetime

import time

if sys.version_info.major == 2:
    import urlparse
else:
    from urllib import parse as urlparse

from genologics.entities import Artifact, ReagentKit, ReagentLot
from genologics.lims import Lims

reagent_kit_map= {
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

__author__ = 'tcezard'

run_path = ''

logger = logging.getLogger(__name__)


def find_run_parameters(run_name):
    if os.path.exists(os.path.join(run_path, run_name)):
        return os.path.join(run_path, run_name, 'run_parameters.xml')


def get_reagent_name_from_run_parameter(run_parameters):
    root = ElementTree.parse(run_parameters).getroot()
    for reagent in root.find('Setup/LimsReagents').getchildren():
        name = reagent.find('ReagentName').text
        lot =  reagent.find('ReagentBarcode').text
        yield  (name, lot)


def create_reagent_for_run(lims, run_name):
    run_parameters = find_run_parameters(run_name)
    for name, lot in get_reagent_name_from_run_parameter(run_parameters):
        reagent_lots = lims.get_reagent_lots(number=lot)
        if len(reagent_lots) == 1:
            reagent_lot = reagent_lots[0]
            if reagent_lot.status != 'active':
                reagent_lot.status = 'active'
                reagent_lot.expiry_date=time.strftime('%Y-%m,-%d')
                reagent_lot.put()
        else:
            reagent_kits = lims.get_reagent_kits(name=reagent_kit_map[name])
            if len(reagent_kits) != 1:
                raise Exception("Found %s reagent kits for name %s"%(len(reagent_kits), reagent_kit_map[name]))
            reagent_lot = ReagentLot.create(reagent_kit=reagent_kits[0], name=name, lot_number=lot,
                                    expiry_date=time.strftime('%Y-%m,-%d'), status='active')


        print('Create reagent %s: %s'(name, lot))



def main():
    args = _parse_args()
    r1 = urlparse.urlsplit(args.step_uri)
    server_http = '%s://%s'%(r1.scheme, r1.netloc)

    #Assume the step_uri contains the step id at the end
    step_id = r1.path.split('/')[-1]
    lims = Lims(server_http, args.username, args.password)

    #setup logging
    level = logging.INFO
    logger.setLevel(level)
    formatter = logging.Formatter(
            fmt='[%(asctime)s] [%(levelname)s] %(message)s',
            datefmt='%Y-%b-%d %H:%M:%S'
        )
    handler = logging.FileHandler(args.log_file)
    handler.setFormatter(formatter)
    handler.setLevel(level)
    logger.addHandler(handler)
    return(create_reagent_for_run(lims, run_name))

def _parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--username', dest="username", type=str, required=True, help='The username of the person logged in')
    p.add_argument('--password', dest="password", type=str, required=True, help='The password used by the person logged in')
    p.add_argument('--step_uri', dest='step_uri', type=str, required=True, help='The uri of the step this EPP is attached to')
    p.add_argument('--log_file', dest='log_file', type=str, required=True, help='The log file containing statement about what was done')
    return p.parse_args()


if __name__ == "__main__":
    sys.exit(main())
