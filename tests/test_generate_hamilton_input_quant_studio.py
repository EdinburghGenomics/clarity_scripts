from itertools import cycle

from scripts.generate_hamilton_input_quant_studio import GenerateHamiltonInputQuantStudio
from tests.test_common import TestEPP, FakeEntitiesMaker


class TestGenerateHamiltonInputQuantStudio(TestEPP):
    def setUp(self):
        # argument -d left blank to write file to local directory
        self.epp = GenerateHamiltonInputQuantStudio(self.default_argv + ['-i', '77-77777'])

        self.epp2 = GenerateHamiltonInputQuantStudio(self.default_argv + ['-i', '11-11111', '22-22222'])

        self.epp3 = GenerateHamiltonInputQuantStudio(self.default_argv + ['-i', '44-44444', '55-55555', '66-66666'])

    def test_1_input_plate(
            self):  # test that file is written under happy path conditions for 1 input plate and 1 output plate
        fem = FakeEntitiesMaker()
        self.epp.lims = fem.lims
        self.epp.process = fem.create_a_fake_process(
            nb_input=2,
            nb_input_container=1,
            nb_output_container=1,
            output_artifact_udf={'Genotyping Sample Volume (ul)': 10, 'Genotyping Buffer Volume (ul)': 50}
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
            input_container_name=cycle(['input_uri_container_%03d' % (i + 1) for i in range(10)]),
            output_artifact_udf={'Genotyping Sample Volume (ul)': 10, 'Genotyping Buffer Volume (ul)': 50}
        )

        self.epp2._run()

        expected_file_1 = [
            'Input Plate,Input Well,Output Plate,Output Well,DNA Volume,TE Volume',
            'input_uri_container_001,A:1,output_uri_container_11,A:1,10,50',
            'input_uri_container_002,A:1,output_uri_container_11,B:1,10,50',
            'input_uri_container_003,A:1,output_uri_container_11,C:1,10,50',
            'input_uri_container_004,A:1,output_uri_container_11,D:1,10,50',
            'input_uri_container_005,A:1,output_uri_container_11,E:1,10,50',
            'input_uri_container_006,A:1,output_uri_container_11,F:1,10,50',
            'input_uri_container_007,A:1,output_uri_container_11,G:1,10,50',
            'input_uri_container_008,A:1,output_uri_container_11,H:1,10,50',
            'input_uri_container_009,A:1,output_uri_container_11,A:2,10,50'
        ]

        expected_file_2 = [
            'Input Plate,Input Well,Output Plate,Output Well,DNA Volume,TE Volume',
            'input_uri_container_010,A:1,output_uri_container_11,B:2,10,50'
        ]

        assert self.file_content('11-11111-hamilton_input_1.csv') == expected_file_1
        assert self.stripped_md5('11-11111-hamilton_input_1.csv') == '6783d5df6c66ac6de1f05775952a599d'

        assert self.file_content('22-22222-hamilton_input_2.csv') == expected_file_2
        assert self.stripped_md5('22-22222-hamilton_input_2.csv') == 'b50140200dc388aa15cf3e97b00f271d'

    def test_27_input_plate(self):
        # test that file is written under happy path conditions for 27 input plates and 1 output plates

        fem = FakeEntitiesMaker()
        self.epp3.lims = fem.lims

        self.epp3.process = fem.create_a_fake_process(
            nb_input=27,
            nb_input_container=27,
            nb_output_container=1,
            input_container_name=cycle(['input_uri_container_%03d' % (i + 1) for i in range(27)]),
            output_artifact_udf={'Genotyping Sample Volume (ul)': 10, 'Genotyping Buffer Volume (ul)': 50}
        )

        self.epp3._run()

        expected_file_1 = [
            'Input Plate,Input Well,Output Plate,Output Well,DNA Volume,TE Volume',
            'input_uri_container_001,A:1,output_uri_container_28,A:1,10,50',
            'input_uri_container_002,A:1,output_uri_container_28,B:1,10,50',
            'input_uri_container_003,A:1,output_uri_container_28,C:1,10,50',
            'input_uri_container_004,A:1,output_uri_container_28,D:1,10,50',
            'input_uri_container_005,A:1,output_uri_container_28,E:1,10,50',
            'input_uri_container_006,A:1,output_uri_container_28,F:1,10,50',
            'input_uri_container_007,A:1,output_uri_container_28,G:1,10,50',
            'input_uri_container_008,A:1,output_uri_container_28,H:1,10,50',
            'input_uri_container_009,A:1,output_uri_container_28,A:2,10,50'
        ]

        expected_file_2 = [
            'Input Plate,Input Well,Output Plate,Output Well,DNA Volume,TE Volume',
            'input_uri_container_010,A:1,output_uri_container_28,B:2,10,50',
            'input_uri_container_011,A:1,output_uri_container_28,C:2,10,50',
            'input_uri_container_012,A:1,output_uri_container_28,D:2,10,50',
            'input_uri_container_013,A:1,output_uri_container_28,E:2,10,50',
            'input_uri_container_014,A:1,output_uri_container_28,F:2,10,50',
            'input_uri_container_015,A:1,output_uri_container_28,G:2,10,50',
            'input_uri_container_016,A:1,output_uri_container_28,H:2,10,50',
            'input_uri_container_017,A:1,output_uri_container_28,A:3,10,50',
            'input_uri_container_018,A:1,output_uri_container_28,B:3,10,50'
        ]

        expected_file_3 = [
            'Input Plate,Input Well,Output Plate,Output Well,DNA Volume,TE Volume',
            'input_uri_container_019,A:1,output_uri_container_28,C:3,10,50',
            'input_uri_container_020,A:1,output_uri_container_28,D:3,10,50',
            'input_uri_container_021,A:1,output_uri_container_28,E:3,10,50',
            'input_uri_container_022,A:1,output_uri_container_28,F:3,10,50',
            'input_uri_container_023,A:1,output_uri_container_28,G:3,10,50',
            'input_uri_container_024,A:1,output_uri_container_28,H:3,10,50',
            'input_uri_container_025,A:1,output_uri_container_28,A:4,10,50',
            'input_uri_container_026,A:1,output_uri_container_28,B:4,10,50',
            'input_uri_container_027,A:1,output_uri_container_28,C:4,10,50'
        ]

        assert self.file_content('44-44444-hamilton_input_1.csv') == expected_file_1
        assert self.stripped_md5('44-44444-hamilton_input_1.csv') == '8197a471462b032301fe6e90cd8d435e'

        assert self.file_content('55-55555-hamilton_input_2.csv') == expected_file_2
        assert self.stripped_md5('55-55555-hamilton_input_2.csv') == 'c673aaf73f965d94cca5a16cf0dc9401'

        assert self.file_content('66-66666-hamilton_input_3.csv') == expected_file_3
        assert self.stripped_md5('66-66666-hamilton_input_3.csv') == 'ea9d72336acad2afec0daf94733eaf6e'
