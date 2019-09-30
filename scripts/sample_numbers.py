#!/usr/bin/env python
import urllib

import dash
import dash_core_components as dcc
import dash_html_components as html

from EPPs.common import StepEPP


class GenerateSampleNumbersGraph(StepEPP):
    # create variables for the months and years to be used in different functions
    months = ['01', '02', '03', '04', '05', '06', '07','08', '09', '10', '11', '12']
    years = ['2015','2016', '2017', '2018', '2019']



    # batch limit function reduces the number of samples in each batch call to prevent server resource error (modified from prepare_discard_plate.py)
    def batch_limit(self, list_instance, max_query=100):
        batch = []
        for start in range(0, len(list_instance), max_query):
            batch = batch + self.lims.get_batch(
                list_instance[start:start + max_query])
        return batch

    def get_sample_numbers(self):

        #dict to store sample numbers by year and month
        sample_numbers={}


        sample_receive_processes= self.lims.get_processes(type=['Sample Receipt EG 1.0 ST',
                                                                      'FluidX Sample Receipt EG 1.1 ST',
                                                                      'Receive Sample EG 6.1',
                                                                      'Receive Sample EG 6.0',
                                                                      'Receive Sample 4.0'])
        for process in sample_receive_processes:
            number_of_samples=len(process.all_inputs(unique=True))
            year_month_run = process.date_run[:7]
            if year_month_run in sample_numbers:
                sample_numbers[year_month_run] = sample_numbers[year_month_run] + number_of_samples
            else:
                sample_numbers[year_month_run] = number_of_samples

        return sample_numbers

    def generate_graph(self,sample_numbers):
        external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

        app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

        # build list of dictionaries for each year to be used in graph data
        years_dictionaries_list = []
        x_axis_titles = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September',
                               'October', 'November', 'December']
        for year in self.years:
            y_values = []
            for month in self.months:
                if year+"-"+month in sample_numbers:
                    y_values.append(sample_numbers[year+"-"+month])
                else:
                    y_values.append(0)

            years_dictionaries_list.append({'x': x_axis_titles, 'y':y_values, 'type': 'bar', 'name': year})


        app.layout = html.Div(children=[
            html.H1(children='Sample Receipt 2015-2019'),

            html.Div(children='''
                Number of Samples Received By Month from 2015 to 2019.
            '''),


            dcc.Graph(
                id='example-graph',

                figure={
                    'data': years_dictionaries_list,
                    'layout': {
                        'title': 'Samples Received'
                    }
                }
            )
        ])
        app.run_server(debug=False)

    def _run(self):
        sample_numbers = self.get_sample_numbers()

        self.generate_graph(sample_numbers)


if __name__ == '__main__':
    GenerateSampleNumbersGraph().run()
