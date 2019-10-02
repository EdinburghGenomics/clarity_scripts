#!/usr/bin/env python
import urllib

import dash
import dash_core_components as dcc
import dash_html_components as html

from EPPs.common import StepEPP


class GenerateSampleNumbersGraph(StepEPP):
    # create variables for the months and years to be used in different functions
    months = ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12']
    years = ['2015', '2016', '2017', '2018', '2019']

    # batch limit function reduces the number of samples in each batch call to prevent server resource error (modified from prepare_discard_plate.py)
    def batch_limit(self, list_instance, max_query=100):
        batch = []
        for start in range(0, len(list_instance), max_query):
            batch = batch + self.lims.get_batch(
                list_instance[start:start + max_query])
        return batch

    def get_sample_numbers(self, process_names_list):

        # find the number of samples received
        # dict to store sample numbers by year and month
        sample_numbers = {}

        # find all the instances of processes used to receive samples
        sample_receive_processes = self.lims.get_processes(type=process_names_list)
        # extract and count the number of samples received present in each process
        for process in sample_receive_processes:
            number_of_samples = len(process.all_inputs(unique=True))
            year_month_run = process.date_run[:7]
            if year_month_run in sample_numbers:
                sample_numbers[year_month_run] = sample_numbers[year_month_run] + number_of_samples
            else:
                sample_numbers[year_month_run] = number_of_samples

        return sample_numbers

    def generate_values(self, x_axis_titles, sample_numbers):
        # create a list of dictionaries per year containing monthly sample counts and the mean. This format can then be plotted by dash.
        # build list of dictionaries for each year to be used in graph data
        years_dictionaries_list = []
        # populate each years dictionary with monthly values
        for year in self.years:
            y_values = []
            for month in self.months:
                if year + "-" + month in sample_numbers:
                    y_values.append(sample_numbers[year + "-" + month])
                else:
                    y_values.append(0)

            years_dictionaries_list.append({'x': x_axis_titles, 'y': y_values, 'type': 'bar', 'name': year})
        # create the monthly means
        means = []
        for month in self.months:
            # create list of the means for each month
            values_for_mean = []
            for year in self.years:
                print(year + "-" + month)
                if year + "-" + month in sample_numbers:
                    values_for_mean.append(sample_numbers[year + "-" + month])
            # calculate mean for the months across the years
            means.append(sum(values_for_mean) / len(self.years))

        # append the mean values to the dictionary
        years_dictionaries_list.append({'x': x_axis_titles, 'y': means, 'type': 'bar', 'name': 'mean'})

        return years_dictionaries_list

    def generate_graph(self, sample_numbers):
        external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

        app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
        x_axis_titles = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September',
                         'October', 'November', 'December']
        sample_received_graph_data = self.generate_values(x_axis_titles, sample_numbers[0])
        data_released_graph_data = self.generate_values(x_axis_titles, sample_numbers[1])

        app.layout = html.Div(children=[
            html.H1(children='Sample Receipt and Data Release 2015-2019'),

            # html.Div(children='''
            #     Number of Samples Received By Month from 2015 to 2019.
            # '''),

            dcc.Graph(
                id='example-graph',

                figure={
                    'data': sample_received_graph_data,
                    'layout': {
                        'title': 'Number of Samples Received By Month 2015 to 2019'
                    }
                }
            ),

            dcc.Graph(
                id='example-graph2',

                figure={
                    'data': data_released_graph_data,
                    'layout': {
                        'title': 'Number of Samples Data Release By Month 2015-2019'
                    }
                }
            )
        ])
        app.run_server(debug=False)

    def _run(self):
        sample_numbers_received = self.get_sample_numbers(['Sample Receipt EG 1.0 ST',
                                                           'FluidX Sample Receipt EG 1.1 ST',
                                                           'Receive Sample EG 6.1',
                                                           'Receive Sample EG 6.0',
                                                           'Receive Sample 4.0'])
        sample_numbers_released = self.get_sample_numbers(['Data Release EG 2.0 ST',
                                                           'Data Release EG 1.0'])

        self.generate_graph([sample_numbers_received, sample_numbers_released])


if __name__ == '__main__':
    GenerateSampleNumbersGraph().run()
