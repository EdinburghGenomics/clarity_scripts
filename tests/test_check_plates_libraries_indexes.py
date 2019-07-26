from itertools import cycle
from unittest.mock import patch, Mock

import pytest

from EPPs.common import InvalidStepError
from scripts.check_plates_libraries_indexes import CheckPlatesLibrariesIndexes
from tests.test_common import TestEPP, FakeEntitiesMaker, NamedMock


class TestCheckPlatesLibrariesIndexes(TestEPP):

    def setUp(self):
        self.epp = CheckPlatesLibrariesIndexes(self.default_argv)
        reagent_types1 = cycle(
            [[NamedMock(real_name='rt1', category='cat1')], [NamedMock(real_name='rt2', category='cat2')]])
        reagent_types2 = Mock(return_value=[NamedMock(real_name='rt1', category='cat1')])
        self.patched_get_reagent_types1 = patch('pyclarity_lims.lims.Lims.get_reagent_types',
                                                side_effect=reagent_types1)
        self.patched_get_reagent_types2 = patch('pyclarity_lims.lims.Lims.get_reagent_types',
                                                side_effect=reagent_types2)

    def test_check_plates_libraries_adapters_too_many_index_categories(self):  # error due to two index categories
        # i.e. reagent_type categories
        fem = FakeEntitiesMaker()

        self.epp.process = fem.create_a_fake_process(nb_input=2, input_reagent_label=['Adapter1'],
                                                     sample_udfs={
                                                         'Prep Workflow': 'TruSeq Nano DNA Library Prep'})

        with self.patched_get_reagent_types1, pytest.raises(InvalidStepError) as e:
            self.epp._run()

        assert e.value.message == "Multiple index types present in step. Only 1 permitted."

    def test_check_plates_libraries_adapters_too_many_prep_workflows(
            self):  # artifacts present where samples have different
        # Prep Workflow udf values
        fem = FakeEntitiesMaker()

        self.epp.process = fem.create_a_fake_process(nb_input=2, input_reagent_label=['Adapter1'],
                                                     sample_udfs={
                                                         'Prep Workflow': cycle(['TruSeq Nano DNA Library Prep',
                                                                                 'TruSeq PCR-Free DNA Library Prep'])})

        with self.patched_get_reagent_types2, pytest.raises(InvalidStepError) as e:
            self.epp._run()

        assert e.value.message == "Multiple library types (Prep Workflow) present in step. Only 1 permitted."
