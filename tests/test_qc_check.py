from unittest.mock import Mock, patch
from scripts.qc_check import QCCheck
from tests.test_common import TestEPP, NamedMock, PropertyMock


fake_input_output_maps =[
                            [{'uri':Mock(id='ai1')},{'uri':Mock(id='ao1', udf={'OutputResult':5}), 'output-generation-type':'PerInput'}],
                            [{'uri':Mock(id='ai2')},{'uri':Mock(id='ao1', udf={'OutputResult':2}), 'output-generation-type':'PerInput'}],
                            [{'uri':Mock(id='ai3')},{'uri':Mock(id='ao1', udf={'OutputResult':9}), 'output-generation-type':'PerInput'}]
                        ]

class TestQCCheck(TestEPP):
    def setUp(self):

        self.patched_process = patch.object(
            QCCheck,
            'process',
            new_callable=PropertyMock(
                return_value=Mock(
                    udf={'StepMinimum': 3, 'StepMaximum': 8},
                    input_output_maps=fake_input_output_maps,
        )))


        self.patched_lims = patch.object(QCCheck, 'lims', new_callable=PropertyMock(return_value=Mock(name='ai')))
        self.epp = QCCheck(self.default_argv + ['-n','StepMinimum', 'StepMaximum']
                           + ['-t', 'OutputResult', 'OutputResult'] + ['-o','>=','<=']
                           + ['-v','OutputResultReview','OutputResultReview'] + ['-w', 'FAIL, output result < minimum','FAIL, output result > maximum'])

        self.epp2 = QCCheck(self.default_argv + ['-n','StepMinimum', 'StepMaximum']
                           + ['-t', 'OutputResult', 'OutputResult'] + ['-o','>=','<=']
                           + ['-v','OutputResultReview','OutputResultReview'] + ['-w', 'FAIL, output result < minimum','FAIL, output result > maximum']+
                           ['-ps','Congratulations'])


    def test_qc_check_happ_path_without_optional_arg(self):
        with self.patched_process, self.patched_lims:
            self.epp._run()

            assert self.epp.process.input_output_maps[0][1]['uri'].udf.get('OutputResultReview')=='PASSED'
            assert self.epp.process.input_output_maps[1][1]['uri'].udf.get('OutputResultReview')=='FAIL, output result < minimum'
            assert self.epp.process.input_output_maps[2][1]['uri'].udf.get('OutputResultReview') == 'FAIL, output result > maximum'

    def test_qc_check_happ_path_with_optional_arg(self):
        with self.patched_process, self.patched_lims:
            self.epp2._run()

            assert self.epp.process.input_output_maps[0][1]['uri'].udf.get('OutputResultReview')=='Congratulations'
            assert self.epp.process.input_output_maps[1][1]['uri'].udf.get('OutputResultReview')=='FAIL, output result < minimum'
            assert self.epp.process.input_output_maps[2][1]['uri'].udf.get('OutputResultReview') == 'FAIL, output result > maximum'
