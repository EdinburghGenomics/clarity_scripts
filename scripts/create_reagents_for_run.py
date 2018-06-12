#!/usr/bin/env python
import os
import sys
import time
from logging import FileHandler
from xml.etree import ElementTree
from pyclarity_lims.entities import ReagentLot
from egcg_core.app_logging import logging_default as log_cfg
from EPPs.common import StepEPP, step_argparser


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


def find_run_parameters(run_name):
    if os.path.exists(os.path.join(run_path, run_name)):
        return os.path.join(run_path, run_name, 'run_parameters.xml')


def get_reagent_name_from_run_parameter(run_parameters):
    root = ElementTree.parse(run_parameters).getroot()
    for reagent in root.find('Setup/LimsReagents').getchildren():
        name = reagent.find('ReagentName').text
        lot = reagent.find('ReagentBarcode').text
        yield (name, lot)


class CreateReagentForRun(StepEPP):
    def __init__(self, step_uri, username, password, run_name):
        super().__init__(step_uri, username, password)
        self.run_name = run_name

    def _run(self):
        run_parameters = find_run_parameters(self.run_name)
        for name, lot in get_reagent_name_from_run_parameter(run_parameters):
            reagent_lots = self.lims.get_reagent_lots(number=lot)
            if len(reagent_lots) == 1:
                reagent_lot = reagent_lots[0]
                if reagent_lot.status != 'active':
                    reagent_lot.status = 'active'
                    reagent_lot.expiry_date = time.strftime('%Y-%m,-%d')
                    reagent_lot.put()
            else:
                reagent_kits = self.lims.get_reagent_kits(name=reagent_kit_map[name])
                if len(reagent_kits) != 1:
                    raise ValueError('Found %s reagent kits for name %s' % (len(reagent_kits), reagent_kit_map[name]))

                ReagentLot.create(
                    self.lims,
                    reagent_kit=reagent_kits[0],
                    name=name,
                    lot_number=lot,
                    expiry_date=time.strftime('%Y-%m,-%d'),
                    status='active'
                )

            print('Created reagent %s: %s' % (name, lot))


def main():
    a = step_argparser()
    a.add_argument('--run_name', type=str)
    args = a.parse_args()
    log_cfg.add_handler(FileHandler(args.log_file))
    action = CreateReagentForRun(args.step_uri, args.username, args.password, args.run_name)
    return action.run()


if __name__ == '__main__':
    sys.exit(main())
