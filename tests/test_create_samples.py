from unittest.mock import patch, Mock, PropertyMock, call

from pyclarity_lims.entities import Sample

from tests.test_common import TestEPP, NamedMock, FakeEntitiesMaker

from scripts.create_samples import CreateSamples, Container

class TestCreateSamples(TestEPP):

    project=NamedMock(real_name='project1')

    container1 = NamedMock(real_name=project.name+'P001', type=NamedMock(real_name='96 well plate'))
    container2 = NamedMock(real_name=project.name+'R01', type=NamedMock(real_name='rack 96 positions'))
    container3 = NamedMock(real_name=project.name+'R01', type=NamedMock(real_name='SGP rack 96 positions'))

    sampleUDF={'[C]Prep Workflow':'-',
                 '[G]Coverage (X)(1)':0}

    sample1 = NamedMock(real_name=container1.name+'A01', project=project, container=container1, udf=sampleUDF)
    artifact1 = Mock(samples=[sample1], container=container1)
    sample1.artifact=artifact1

    process_udf={'Container Type':'96 well plate',
                 'Plate Suffix':'P{0-9}[3]',
                 'Number in Group 1':1,
                 'Number in Group 2':0,
                 'Number in Group 3':0,
                 'Number in Group 4':0,
                 '[C]Prep Workflow':'TruSeq Nano DNA Sample Prep',
                 '[G]Coverage (X)(1)':30,
                 'Next Workflow':'A workflow',
                 'Next Step':'A step'}

    process_udf2=process_udf
    process_udf2['Number in Group 1']=2

    process_udf3={'Container Type':'96 well plate',
                 'Plate Suffix':'P{0-9}[3]',
                 'Number in Group 1':2,
                 'Number in Group 2':1,
                 'Number in Group 3':1,
                 'Number in Group 4':1,
                 '[C]Prep Workflow':'TruSeq Nano DNA Sample Prep',
                 '[G]Coverage (X)(1)':30,
                  '[G]Coverage (X)(2)': 60,
                  '[G]Coverage (X)(3)': 90,
                  '[G]Coverage (X)(4)': 120,
                 'Next Workflow':'A workflow',
                 'Next Step':'A step'}

    patched_process = patch.object(
        CreateSamples,
        'process',
        new_callable=PropertyMock(return_value=Mock(
            all_inputs=Mock(return_value=[artifact1]),
            udf=process_udf
        ))
    )

    patched_process2 = patch.object(
        CreateSamples,
        'process',
        new_callable=PropertyMock(return_value=Mock(
            all_inputs=Mock(return_value=[artifact1]),
            udf=process_udf2
        ))
    )

    patched_process3 = patch.object(
        CreateSamples,
        'process',
        new_callable=PropertyMock(return_value=Mock(
            all_inputs=Mock(return_value=[artifact1]),
            udf=process_udf3
        ))
    )

    patched_get_workflow_stage = patch(
        'scripts.create_samples.get_workflow_stage',
        return_value=Mock(uri='a_uri')
    )

    patched_create_batch = patch(
        'lims.create_samples.create_batch',
        return_value=True
    )



    def setUp(self):

        self.epp=CreateSamples(self.default_argv)

    def test_create_sample_96_well_plate_1_sample(self): # no new samples created, input sample populated by step UDFs
        fem = FakeEntitiesMaker()
        self.epp.lims = fem.lims
        self.epp.process = fem.create_a_fake_process(
            project_name='X99999',
            input_container_name='X99999P001',
            sample_name='X99999P001A01',
            output_per_input=0,
            step_udfs={
                'Container Type': '96 well plate',
                'Plate Suffix': 'P[0-9]{3}',
                'Number in Group 1': 96,
                'Number in Group 2': 0,
                'Number in Group 3': 0,
                'Number in Group 4': 0,
                '[C]Prep Workflow': 'TruSeq Nano DNA Sample Prep',
                '[G]Coverage (X)(1)': 30,
                'Next Workflow': 'A workflow',
                'Next Step': 'A step'
            }
        )
        self.epp.lims.get_containers = Mock(side_effect=[['something'], ['something'], []])
        with self.patched_get_workflow_stage:
            self.epp._validate_step()
            self.epp._run()

        assert self.epp.artifacts[0].samples[0].udf == {
            'Coverage (X)': 30,
            'Prep Workflow': 'TruSeq Nano DNA Sample Prep'
        }


        # with self.patched_process, self.patched_lims,self.patched_get_workflow_stage:
        #     self.epp._run()
        #     #check that a step UDF with the [C] tag populates the matching sample UDF
        #     assert self.epp.artifacts[0].samples[0].udf['Prep Workflow'] == self.epp.process.udf['[C]Prep Workflow']
        #     #check that a step UDF with the [G] tag and group number populates the matching sample UDF
        #     assert self.epp.artifacts[0].samples[0].udf['Coverage (X)'] == self.epp.process.udf['[G]Coverage (X)(1)']

    def test_create_sample_96_well_plate_2_sample(self): # 1 new sample created
        with self.patched_process2, self.patched_lims, self.patched_get_workflow_stage as pws:
            self.epp._run()

            #check that a new sample is created with sample UDFs populated by step UDFs
            self.epp.lims.create_batch.assert_called_with(Sample,[{'container': self.container1,
                                                                   'project': self.project,
                                                                   'name': self.container1.name+'B01',
                                                                   'position': 'B:01',
                                                                   'udf':
                                                                       {'Prep Workflow': 'TruSeq Nano DNA Sample Prep',
                                                                        'Coverage (X)': 30}}])

            # check that a newly created sample is assigned to workflow step
            pws.assert_called_with(
                self.epp.lims, 'A workflow', 'A step'
            )

    def test_create_sample_96_well_plate_4_new_samples(self): # 1 new sample created in each of 4 groups
        with self.patched_process3, self.patched_lims, self.patched_get_workflow_stage as pws:
            self.epp._run()

            #check that a new sample is created with sample UDFs populated by step UDFs
            self.epp.lims.create_batch.assert_called_with(Sample,[{'container': self.container1,
                                                                   'project': self.project,
                                                                   'name': self.container1.name+'B01',
                                                                   'position': 'B:01',
                                                                   'udf':
                                                                       {'Prep Workflow': 'TruSeq Nano DNA Sample Prep',
                                                                        'Coverage (X)': 30}},
                                                                  {'container': self.container1,
                                                                   'project': self.project,
                                                                   'name': self.container1.name + 'C01',
                                                                   'position': 'C:01',
                                                                   'udf':
                                                                       {'Prep Workflow': 'TruSeq Nano DNA Sample Prep',
                                                                        'Coverage (X)': 60}},
                                                                  {'container': self.container1,
                                                                   'project': self.project,
                                                                   'name': self.container1.name + 'D01',
                                                                   'position': 'D:01',
                                                                   'udf':
                                                                       {'Prep Workflow': 'TruSeq Nano DNA Sample Prep',
                                                                        'Coverage (X)': 90}},
                                                                  {'container': self.container1,
                                                                   'project': self.project,
                                                                   'name': self.container1.name + 'E01',
                                                                   'position': 'E:01',
                                                                   'udf':
                                                                       {'Prep Workflow': 'TruSeq Nano DNA Sample Prep',
                                                                        'Coverage (X)': 120}}
                                                                  ])

            # check that a newly created sample is assigned to workflow step
            pws.assert_called_with(
                self.epp.lims, 'A workflow', 'A step'
            )