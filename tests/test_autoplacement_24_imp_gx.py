from unittest.mock import Mock, patch, PropertyMock

import pytest
from EPPs.common import InvalidStepError
from scripts.autoplacement_24_imp_gx import Autoplacement24IMPGX
from tests.test_common import TestEPP, NamedMock

fake_selected_containers = [Mock(id='c1'),Mock(id='c2')]

fake_outputs_per_input = [Mock(id='ao1', container='Container1', location=''),
                           Mock(id='ao2', container='Container1', location='')]

fake_outputs_per_input2 = [Mock(id='ao1', container='Container1', location=''),
                          Mock(id='ao2', container='Container1', location=''),
                          Mock(id='ao3', container='Container1', location='')]

fake_inputs = [
    NamedMock(real_name="ai1 name", id='ai1', type='Analyte', container='container1',
              location=('container1', 'A:1')),
    NamedMock(real_name="ai2 name", id='ai2', type='Analyte', container='container1',
              location=('container1', 'B:1'))
]

fake_inputs2 = [
    NamedMock(real_name="ai1 name", id='ai1', type='Analyte', container='container1',
              location=('container1', 'A:1')),
    NamedMock(real_name="ai2 name", id='ai2', type='Analyte', container='container2',
              location=('container2', 'B:1'))
]


def fake_inputs3(unique=True):
    max_inputs = 25
    input_counter = 1
    inputs_list = []
    while input_counter <= max_inputs:
        inputs_list.append(Mock(id='ai' + str(input_counter)))
        input_counter += 1

    return inputs_list


class TestAutoplacement24IMPGX(TestEPP):
    def setUp(self):
        self.patched_process1 = patch.object(
            Autoplacement24IMPGX,
            'process',
            new_callable=PropertyMock(
                return_value=Mock(
                    all_inputs=Mock(return_value=fake_inputs),
                    outputs_per_input=Mock(return_value=fake_outputs_per_input),
                    step=Mock(
                        id='s1',
                        placements=Mock(id='p1',selected_containers=fake_selected_containers))
                    )
                )
            )

        self.patched_process2 = patch.object(
            Autoplacement24IMPGX,
            'process',
            new_callable=PropertyMock(
                return_value=Mock(
                    all_inputs=Mock(return_value=fake_inputs),
                    outputs_per_input=Mock(return_value=fake_outputs_per_input2),
                    step=Mock(
                        id='s1',
                        placements=Mock(id='p1',selected_containers=fake_selected_containers))
                    )
                )
            )

        self.patched_process3= patch.object(
            Autoplacement24IMPGX,
            'process',
            new_callable=PropertyMock(
                return_value=Mock(
                    all_inputs=fake_inputs3,
                    outputs_per_input=Mock(return_value=fake_outputs_per_input),
                    step=Mock(
                        id='s1',
                        placements=Mock(id='p1',selected_containers=fake_selected_containers))
                    )
                )
            )

        self.patched_process4= patch.object(
            Autoplacement24IMPGX,
            'process',
            new_callable=PropertyMock(
                return_value=Mock(
                    all_inputs=Mock(return_value=fake_inputs2),
                    outputs_per_input=Mock(return_value=fake_outputs_per_input),
                    step=Mock(
                        id='s1',
                        placements=Mock(id='p1',selected_containers=fake_selected_containers))
                    )
                )
            )

        # self.patched_process2 = patch.object(
        #     Autoplacement24IMPGX,
        #     'process',
        #     new_callable=PropertyMock(
        #         return_value=Mock(
        #             all_inputs=Mock(return_value=fake_inputs2),
        #             outputs_per_input=Mock(return_value=fake_outputs_per_input2),
        #             step=Mock(
        #                 id='s1',
        #                 placements=Mock(id='p1', get_selected_containers=Mock(return_value=fake_selected_containers))
        #             )
        #         )
        #     )
        # )
        #
        # self.patched_process3 = patch.object(
        #     Autoplacement24IMPGX,
        #     'process',
        #     new_callable=PropertyMock(
        #         return_value=Mock(
        #             all_inputs=Mock(return_value=fake_inputs2),
        #             outputs_per_input=Mock(return_value=fake_outputs_per_input),
        #             step=Mock(
        #                 id='s1',
        #                 placements=Mock(id='p1', get_selected_containers=Mock(return_value=fake_selected_containers))
        #             )
        #         )
        #     )
        # )
        #
        # self.patched_process4 = patch.object(
        #     Autoplacement24IMPGX,
        #     'process',
        #     new_callable=PropertyMock(
        #         return_value=Mock(
        #             all_inputs=Mock(return_value=fake_inputs3()),
        #             outputs_per_input=Mock(return_value=fake_outputs_per_input),
        #             step=Mock(
        #                 id='s1',
        #                 placements=Mock(id='p1', get_selected_containers=Mock(return_value=fake_selected_containers))
        #             )
        #         )
        #     )
        # )

        self.patched_lims = patch.object(Autoplacement24IMPGX, 'lims', new_callable=PropertyMock)

        self.epp = Autoplacement24IMPGX(self.default_argv)

    def test_autoplacement_qPCR_384_happy_path(self):
        # per input
        with self.patched_process1, self.patched_lims:
            self.epp._run()

            expected_output_placement = [
                (fake_outputs_per_input[0], (fake_selected_containers[0], 'A:1')),
                (fake_outputs_per_input[1], (fake_selected_containers[1], 'A:1')),
                (fake_outputs_per_input[0], (fake_selected_containers[0], 'B:1')),
                (fake_outputs_per_input[1], (fake_selected_containers[1], 'C:1')),
            ]
            self.epp.process.step.set_placements.assert_called_with(fake_selected_containers, expected_output_placement)

    def test_autoplacement_qPCR_384_2_replicates(self):  # 3 replicate outputs rather than required 2
        # per input
        with self.patched_process2, self.patched_lims:
            with pytest.raises(InvalidStepError) as e:
                self.epp._run()
            assert e.value.message =="2 replicates required for each sample and standard. 3 replicates found."


    def test_autoplacement_qPCR_384_more_than_24_inputs(self):  # >24 samples
        with self.patched_process3, self.patched_lims:
            with pytest.raises(InvalidStepError) as e:
                self.epp._run()
            assert e.value.message =="Maximum number of inputs is 24. 25 inputs present in step"

    def test_autoplacement_qPCR_384_more_than_1_input_plates(self):  # >1 input plates
        with self.patched_process4, self.patched_lims:
            with pytest.raises(InvalidStepError) as e:
                self.epp._run()

            assert e.value.message =='2 input containers found. Only 1 input container permissable.'