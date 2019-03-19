from scripts.generate_hamilton_input_quant_studio import GenerateHamiltonInputQuantStudio
from tests.test_common import TestEPP, FakeEntitiesMaker


class TestGenerateHamiltonInputCFP(TestEPP):
    def setUp(self):
        # argument -d left blank to write file to local directory
        self.epp = GenerateHamiltonInputQuantStudio(self.default_argv + ['-i', '77-77777'] + ['-j', '88-88888'] +
                                                    ['-k', '99-99999'])

        self.epp2 = GenerateHamiltonInputQuantStudio(self.default_argv + ['-i', '11-11111'] + ['-j', '22-22222'] +
                                                     ['-k', '33-33333'])

        self.epp3 = GenerateHamiltonInputQuantStudio(self.default_argv + ['-i', '44-44444'] + ['-j', '55-55555'] +
                                                     ['-k', '66-66666'])

    def test_1_input_plate(
            self):  # test that file is written under happy path conditions for 1 input plate and 1 output plate
        fem = FakeEntitiesMaker()
        self.epp.lims = fem.lims
        self.epp.process = fem.create_a_fake_process(
            nb_input=2,
            nb_input_container=1,
            nb_output_container=1,
            output_artifact_udf={'Genotyping Sample Volume (ul)': '10', 'Genotyping Buffer Volume': '50'}
        )

        self.epp._run()

        expected_file = [
            'Input Plate,Input Well,Output Plate,Output Well,DNA Volume,TE Volume',
            'input_uri_container_1,A:1,output_uri_container_2,A:1,10,50',
            'input_uri_container_1,B:1,output_uri_container_2,B:1,10,50'
        ]

        assert self.file_content('77-77777-hamilton_input_1.csv') == expected_file
        assert self.stripped_md5('77-77777-hamilton_input_1.csv') == '738f20774b9512b6a65192e7670d88fd'

    def test_10_input_plate(self):
        # test that file is written under happy path conditions for 10 input plates and 1 output plates
        fem = FakeEntitiesMaker()
        self.epp2.lims = fem.lims
        self.epp2.process = fem.create_a_fake_process(
            nb_input=10,
            nb_input_container=10,
            nb_output_container=1,
            output_artifact_udf={'Genotyping Sample Volume (ul)': '10', 'Genotyping Buffer Volume': '50'}
        )

        self.epp2._run()

        expected_file_1 = [
            'Input Plate,Input Well,Output Plate,Output Well,DNA Volume,TE Volume',
            'input_uri_container_1,A:1,output_uri_container_11,A:1,10,50',
            'input_uri_container_10,A:1,output_uri_container_11,B:2,10,50',
            'input_uri_container_2,A:1,output_uri_container_11,B:1,10,50',
            'input_uri_container_3,A:1,output_uri_container_11,C:1,10,50',
            'input_uri_container_4,A:1,output_uri_container_11,D:1,10,50',
            'input_uri_container_5,A:1,output_uri_container_11,E:1,10,50',
            'input_uri_container_6,A:1,output_uri_container_11,F:1,10,50',
            'input_uri_container_7,A:1,output_uri_container_11,G:1,10,50',
            'input_uri_container_8,A:1,output_uri_container_11,H:1,10,50'
        ]

        expected_file_2 = [
            'Input Plate,Input Well,Output Plate,Output Well,DNA Volume,TE Volume',
            'input_uri_container_9,A:1,output_uri_container_11,A:2,10,50',
        ]

        assert self.file_content('11-11111-hamilton_input_1.csv') == expected_file_1
        assert self.stripped_md5('11-11111-hamilton_input_1.csv') == '707ad37393ee90d1d58ee64f93cc57cf'

        assert self.file_content('22-22222-hamilton_input_2.csv') == expected_file_2
        assert self.stripped_md5('22-22222-hamilton_input_2.csv') == '55df133100d2d052935d3ce00605e172'

    def test_27_input_plate(self):
        # test that file is written under happy path conditions for 27 input plates and 1 output plates
        fem = FakeEntitiesMaker()
        self.epp3.lims = fem.lims
        self.epp3.process = fem.create_a_fake_process(
            nb_input=27,
            nb_input_container=27,
            nb_output_container=1,
            output_artifact_udf={'Genotyping Sample Volume (ul)': '10', 'Genotyping Buffer Volume (ul)': '50'}
        )

        self.epp3._run()

        expected_file_1 = [
            'Input Plate,Input Well,Output Plate,Output Well,DNA Volume,TE Volume',
            'input_uri_container_1,A:1,output_uri_container_28,A:1,10,50',
            'input_uri_container_10,A:1,output_uri_container_28,B:2,10,50',
            'input_uri_container_11,A:1,output_uri_container_28,C:2,10,50',
            'input_uri_container_12,A:1,output_uri_container_28,D:2,10,50',
            'input_uri_container_13,A:1,output_uri_container_28,E:2,10,50',
            'input_uri_container_14,A:1,output_uri_container_28,F:2,10,50',
            'input_uri_container_15,A:1,output_uri_container_28,G:2,10,50',
            'input_uri_container_16,A:1,output_uri_container_28,H:2,10,50',
            'input_uri_container_17,A:1,output_uri_container_28,A:3,10,50'
        ]

        expected_file_2 = [
            'Input Plate,Input Well,Output Plate,Output Well,DNA Volume,TE Volume',
            'input_uri_container_18,A:1,output_uri_container_28,B:3,10,50',
            'input_uri_container_19,A:1,output_uri_container_28,C:3,10,50',
            'input_uri_container_2,A:1,output_uri_container_28,B:1,10,50',
            'input_uri_container_20,A:1,output_uri_container_28,D:3,10,50',
            'input_uri_container_21,A:1,output_uri_container_28,E:3,10,50',
            'input_uri_container_22,A:1,output_uri_container_28,F:3,10,50',
            'input_uri_container_23,A:1,output_uri_container_28,G:3,10,50',
            'input_uri_container_24,A:1,output_uri_container_28,H:3,10,50',
            'input_uri_container_25,A:1,output_uri_container_28,A:4,10,50'
        ]

        expected_file_3 = [
            'Input Plate,Input Well,Output Plate,Output Well,DNA Volume,TE Volume',
            'input_uri_container_26,A:1,output_uri_container_28,B:4,10,50',
            'input_uri_container_27,A:1,output_uri_container_28,C:4,10,50',
            'input_uri_container_3,A:1,output_uri_container_28,C:1,10,50',
            'input_uri_container_4,A:1,output_uri_container_28,D:1,10,50',
            'input_uri_container_5,A:1,output_uri_container_28,E:1,10,50',
            'input_uri_container_6,A:1,output_uri_container_28,F:1,10,50',
            'input_uri_container_7,A:1,output_uri_container_28,G:1,10,50',
            'input_uri_container_8,A:1,output_uri_container_28,H:1,10,50',
            'input_uri_container_9,A:1,output_uri_container_28,A:2,10,50'
        ]

        assert self.file_content('44-44444-hamilton_input_1.csv') == expected_file_1
        assert self.stripped_md5('44-44444-hamilton_input_1.csv') == '2565f88d7417f1392e9f4581d5189d2b'

        assert self.file_content('55-55555-hamilton_input_2.csv') == expected_file_2
        assert self.stripped_md5('55-55555-hamilton_input_2.csv') == 'a3dbffb2feeaccd6e338f10071373787'

        assert self.file_content('66-66666-hamilton_input_3.csv') == expected_file_3
        assert self.stripped_md5('66-66666-hamilton_input_3.csv') == 'a32ce093ab9e4114e6f08a5832005e68'
