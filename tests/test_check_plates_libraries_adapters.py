from unittest.mock import patch

import pytest

from EPPs.common import InvalidStepError
from scripts.check_plates_libraries_adapters import CheckPlatesLibrariesAdapters
from tests.test_common import TestEPP, FakeEntitiesMaker, NamedMock


class TestCheckPlatesLibrariesAdapters(TestEPP):

    def setUp(self):
        self.epp = CheckPlatesLibrariesAdapters(self.default_argv)
        reagent_types = iter([[NamedMock(real_name='rt1')], [NamedMock(real_name='rt2')]])
        self.patched_get_reagent_types = patch('pyclarity_lims.lims.Lims.get_reagent_types',
                                               side_effect=reagent_types)

    def test_check_plates_libraries_adapters_too_many_adapters(self):
        fem = FakeEntitiesMaker()
        self.epp.lims = fem.lims
        self.epp.process = fem.create_a_fake_process(nb_input=2, input_reagent_label=['Adapter1', 'Adapter2'])
        with pytest.raises(InvalidStepError) as e:
            self.epp._run()

        assert e.value.message == "Multiple reagent labels present (adapters) on artifact input_art_A:1. Only 1 permitted"

    def test_check_plates_libraries_adapters_too_many_reagent_categories(self):
        fem = FakeEntitiesMaker()
        self.epp.lims = fem.lims
        self.epp.process = fem.create_a_fake_process(nb_input=2, input_reagent_label=['Adapter1', 'Adapter2'])
        with pytest.raises(InvalidStepError) as e:
            self.epp._run()

        assert e.value.message == "Multiple reagent labels present (adapters) on artifact input_art_A:1. Only 1 permitted"

    def test_check_plates_libraries_adapters_too_many_reagent_categories(self):
        fem = FakeEntitiesMaker()

        self.epp.process = fem.create_a_fake_process(nb_input=2, input_reagent_label=['Adapter1'])
        with self.patched_get_reagent_types, pytest.raises(InvalidStepError) as e:
            self.epp._run()

        assert e.value.message == "Multiple adapter types present in step. Only 1 permitted."
