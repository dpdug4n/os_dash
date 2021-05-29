import dash
import dash_table
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd

from app import app
from apps.navbar import Navbar
from utils.maps_tables import running_processes
from utils.inquire import host_queries 

pid_tree_df = pd.DataFrame(columns=['name','parent','pid'])
pid_tree_ColNames=['Name', 'Parent ID', 'Process ID']
r_p_table = running_processes.qresults
r_p_ColNames = ['Start Time', 'Name', 'ProcessID', 'Command', 'Path', 'Current Working Directory','State', 'On Disk']
nav = Navbar()

body = dbc.Container([
    dbc.Row(
            [dbc.Col(
                [html.H2("Running Processes"),
                ])
            ]
        ),
    dbc.Row([
        dbc.Col(html.Div([
            dash_table.DataTable(
                id='running_process_table',
                columns=[{"name": x, "id": y} for x,y in zip(r_p_ColNames,r_p_table.columns)],
                data=r_p_table.to_dict('records'),
                filter_action='native',
                sort_mode = 'multi',
                sort_action='native',
                row_deletable=True,
                fixed_rows={'headers':True},
                style_table={'overflowX': 'scroll'},
                style_cell={
                    'overflow':'hidden',
                    'textOverflow': 'ellipsis', 
                    'textAlign': 'left', 
                    'maxWidth':400,
                    'minWidth':80
                    },
                tooltip_data=[
                    {
                        column: {'value': str(value), 'type': 'markdown'}
                        for column, value in row.items() if len(str(value)) >=50
                    } for row in r_p_table.to_dict('records')
                ],
            )
        ], style={'margin':'2.5px'}),width = 12),
    ]),
    dbc.Row([
        dbc.Col(html.Div([
            html.H5("Process Tree"),
            dash_table.DataTable(
                id='running_process_pidtreetable',
                columns=[{"name": n, "id": x} for n,x in zip(pid_tree_ColNames,pid_tree_df.columns)],
                data=pid_tree_df.to_dict('records'),
                style_cell={'textAlign': 'left'},
                style_table={'overflowX': 'scroll'},
            )
        ], style={'margin':'2.5px'}), width = 6),
        dbc.Col(html.Div([
            html.H5("Frequency Filter"),
            dcc.Slider(
                id='frequency_slider',
                min = 0,
                max = 1,
                step = .0025,
                value = 1
            ),
            html.Div(id='slider-output-container'),
        ]))
    ])
])

layout = html.Div([
    nav,
    body
])

#highlight active cell & it's row
@app.callback(
    Output("running_process_table", "style_data_conditional"),
    Input('running_process_table', 'active_cell'),
)
def style_selected_row(active_cell):
    if active_cell is None:
        return dash.no_update
    return [
        {"if": {'row_index':active_cell['row']},'backgroundColor':'rgba(0, 116, 217, 0.3)'},
    ]

#update pidtree table from selected pid
@app.callback(
    Output('running_process_pidtreetable', 'data'),
    [Input('running_process_table', 'active_cell'),
    State('running_process_table', 'data')]
)
def update_pidtree_table(active_cell, data):
    if active_cell:
        row = active_cell['row']
        pid = data[row]['pid']
        host_queries.pidtree(pid)
        return host_queries.pidtreeresults.to_dict('records')

@app.callback(
    Output("running_process_table", "data"),
    [Input('frequency_slider', 'value'),])
def filter_running_processes(value):
    if value == 1:
        return dash.no_update
    if value is None:
        return dash.no_update
    filtered_r_p_table = pd.DataFrame()
    frequency = r_p_table['name'].value_counts(normalize=True)
    for index, process_frequency in frequency.iteritems():
        if process_frequency >= value:
            filtered_r_p_table = r_p_table[~r_p_table.name.str.contains(index)]
    return filtered_r_p_table.to_dict('records')
            #need to fix this function's logic

@app.callback(
    Output('slider-output-container', 'children'),
    [Input('frequency_slider', 'drag_value'),])
def slider_value_div(value):
    return value

