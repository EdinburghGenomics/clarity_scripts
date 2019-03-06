from unittest.mock import Mock, patch
from scripts.qc_check import QCCheck
from tests.test_common import TestEPP, NamedMock, PropertyMock

#Mocked input artifacts

input1=NamedMock(real_name='Sample1',id='ai1', udf={'Result': 5})
input2=NamedMock(real_name='Sample2',id='ai2', udf={'Result': 2})
input3= NamedMock(real_name='Sample3',id='ai3', udf={'Result': 9})

output1=NamedMock(real_name='Sample1',id='ao1', udf={'Result':5})
output2=NamedMock(real_name='Sample1',id='ao2', udf={'Result':2})
output3=NamedMock(real_name='Sample1',id='ao3', udf={'Result':9})

fake_input_output_maps =[
                            [{'uri':input1},{'uri':output1, 'output-generation-type':'PerInput'}],
                            [{'uri':input2},{'uri':output2, 'output-generation-type':'PerInput'}],
                            [{'uri':input3},{'uri':output3, 'output-generation-type':'PerInput'}]
                        ]

fake_all_inputs = [
    input1,
    input2,
    input3
]


class TestQCCheck(TestEPP):
    def setUp(self):

        self.patched_process = patch.object(
            QCCheck,
            'process',
            new_callable=PropertyMock(
                return_value=Mock(
                    udf={'StepMinimum': 3, 'StepMaximum': 8},
                    input_output_maps=fake_input_output_maps,all_inputs=Mock(return_value=fake_all_inputs)
        )))

        self.patched_lims = patch.object(QCCheck, 'lims', new_callable=PropertyMock(return_value=Mock(name='ai')))
        self.epp = QCCheck(
            self.default_argv
            + ['-n','StepMinimum', 'StepMaximum']
            + ['-t', 'Result', 'Result']
            + ['-o','>=', '<=']
            + ['-v','ResultReview', 'ResultReview']
            + ['-w', 'FAIL, result < minimum', 'FAIL, result > maximum']
        )

        self.epp2 = QCCheck(
            self.default_argv
            + ['-n', 'StepMinimum', 'StepMaximum']
            + ['-t', 'Result', 'Result']
            + ['-o', '>=','<=']
            + ['-v', 'ResultReview', 'ResultReview']
            + ['-w', 'FAIL, result < minimum', 'FAIL, result > maximum']
            + ['-d', 'Congratulations']
        )

        self.epp3 = QCCheck(
            self.default_argv
            + ['-n', 'StepMinimum', 'StepMaximum']
            + ['-t', 'Result', 'Result']
            + ['-o', '>=', '<=']
            + ['-v', 'ResultReview', 'ResultReview']
            + ['-w', 'FAIL, result < minimum', 'FAIL, result > maximum']
            + ['-ci']
        )

    def test_qc_check_happ_path_no_optional(self):
        """test with no optional arguments"""
        with self.patched_process, self.patched_lims:
            self.epp._run()

            assert self.epp.process.input_output_maps[0][1]['uri'].udf.get('ResultReview') == 'PASSED'
            assert self.epp.process.input_output_maps[1][1]['uri'].udf.get('ResultReview') == 'FAIL, result < minimum'
            assert self.epp.process.input_output_maps[2][1]['uri'].udf.get('ResultReview') == 'FAIL, result > maximum'

    def test_qc_check_happ_path_with_passed(self):
        """test with 'passed' value configured"""
        with self.patched_process, self.patched_lims:
            self.epp2._run()

            assert self.epp.process.input_output_maps[0][1]['uri'].udf.get('ResultReview') == 'Congratulations'
            assert self.epp.process.input_output_maps[1][1]['uri'].udf.get('ResultReview') == 'FAIL, result < minimum'
            assert self.epp.process.input_output_maps[2][1]['uri'].udf.get('ResultReview') == 'FAIL, result > maximum'

    def test_qc_check_happ_path_with_ci(self):
        """test with optional check inputs argument"""
        with self.patched_process, self.patched_lims:
            self.epp3._run()

            assert self.epp.process.all_inputs()[0].udf.get('ResultReview') == 'PASSED'
            assert self.epp.process.all_inputs()[1].udf.get('ResultReview') == 'FAIL, result < minimum'
            assert self.epp.process.all_inputs()[2].udf.get('ResultReview') == 'FAIL, result > maximum'
