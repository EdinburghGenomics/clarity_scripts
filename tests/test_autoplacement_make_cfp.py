from unittest.mock import Mock, patch, PropertyMock

from scripts.autoplacement_make_cfp import AutoplacementMakeCFP
from tests.test_common import TestEPP


#def fake_outputs_per_input(inputid, Analyte=True):
 #   fake_outputs={
  #      'ai1': [Mock(id='ao1', container='Container1', location='')],
   #     'ai2': [Mock(id='ao2', container='Container1', location='')]
    #}
    #return (
     #   fake_outputs[inputid]
    #)

fake_selected_containers=[Mock(id='c1')]
fake_outputs_per_input=[Mock(id='ao1', container='Container1', location='')]


class TestAutoplacementMakeCFP(TestEPP):
    def setUp(self):

        fake_inputs = [
            Mock(id='ai1', type='Analyte',output=[Mock(id='ao1', type='Analyte', container='Container1', location='')]),
            Mock(id='ai2', type='Analyte', output=[Mock(id='ao2', type='Analyte', container='Container1', location='')])

        ]



        self.patched_process1 = patch.object(
            AutoplacementMakeCFP,
            'process',
            new_callable=PropertyMock(
                return_value=Mock(
                    all_inputs=Mock(return_value=fake_inputs),
                    outputs_per_input=Mock(return_value=fake_outputs_per_input),
                    step=Mock(
                        id='s1',
                        placements=Mock(id='p1', get_selected_containers=Mock(return_value=fake_selected_containers))
                    )
                )
            )
        )

        self.patched_lims = patch.object(AutoplacementMakeCFP, 'lims', new_callable=PropertyMock)

        self.epp = AutoplacementMakeCFP(
            self.default_argv)

    def test_automated_placement_make_cfp(self):
        # per input
        with self.patched_process1, self.patched_lims:
            self.epp._run()

            expected_output_placement = [
                (fake_outputs_per_input[0], (fake_selected_containers[0], 'A:1')),
                (fake_outputs_per_input[0], (fake_selected_containers[0], 'B:1' ))
            ]
            self.epp.process.step.set_placements.assert_called_with(fake_selected_containers, expected_output_placement)
            #assert self.epp.process.step.get_placement_list == ['']
