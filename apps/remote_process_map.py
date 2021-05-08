import dash
import dash_table
import dash_daq as daq
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd

from app import app
from apps.navbar import Navbar
from utils.inquire import host_queries 
from utils.maps_tables import remote_process_map

remote_process_map = remote_process_map()
remote_process_map.gen_map()
fig = remote_process_map.fig 
tbl = remote_process_map.qresults
tbl = tbl.drop(['local_address','srcLatitude','srcLongitude','Longitude','Latitude'], axis =1)
df = pd.DataFrame(columns=['name','parent','pid'])
pmColNames=['Local Port','Name','Process ID','Remote Address','Remote Port','Abuse Rating','Domain']
ptColNames=['Name', 'Parent ID', 'Process ID']

nav = Navbar()
body = dbc.Container([
    dbc.Row(
        dbc.Col(html.Div([
            dcc.Graph(
                id='remote_process_map',
                figure=fig
            )
            ], style={'margin':'5px'}), width = 12), justify='center'
    ),
    dbc.Row(dbc.Col(html.Div(
        daq.ToggleSwitch(
            id='remote_map_toggle',
            label = "   GreyNoise <-> AbuseIPDB",
            labelPosition = 'bottom',
            value = False,
            persistence = True,
            persistence_type = 'session'
        )
    ), width={"size": 3.5, "offset": 0},#width={"size:"3.5, "offset":1}
    )),
    dbc.Row([
        dbc.Col(html.Div([
            html.H5('Processes with remote connections.'),
            dash_table.DataTable(
                id='processmaptable',
                columns=[{"name": n, "id": x} for n,x in zip(pmColNames,tbl.columns)],
                data=tbl.to_dict('records'),
                filter_action='native',
                sort_mode = 'multi',
                sort_action='native',
                fixed_rows={'headers':True},
                style_table={'overflowX': 'scroll'},
                style_cell={
                    'textAlign': 'left', 
                    'minWidth':125
                    },
            )
        ], style={'margin':'2.5px'}),width = 8),

        dbc.Col(html.Div([
            html.H5('Process Tree'),
            dash_table.DataTable(
                id='pidtreetable',
                columns=[{"name": n, "id": x} for n,x in zip(ptColNames,df.columns)],
                data=df.to_dict('records'),
                style_cell={'textAlign': 'left'},
                style_table={'overflowX': 'scroll'},
            )
        ], style={'margin':'2.5px'}), width = 4)
    ], no_gutters=True)
])

layout = html.Div([ 
    nav,
    body
])



#update pidtree table from table selection
@app.callback(
    Output('pidtreetable', 'data'),
    [Input('processmaptable', 'active_cell'),
    State('processmaptable', 'data')]
)
def update_pidtree_table(active_cell, data):
    if active_cell:
        row = active_cell['row']
        pid = data[row]['pid']
        host_queries.pidtree(pid)
        return host_queries.pidtreeresults.to_dict('records')

#highlight selected row
@app.callback(
    Output("processmaptable", "style_data_conditional"),
    Input('processmaptable', 'active_cell'),
)
def style_selected_row(active_cell):
    if active_cell is None:
        return dash.no_update
    return [
        {"if": {'row_index':active_cell['row']},'backgroundColor':'rgba(0, 116, 217, 0.3)'},
        {'if': {'state': 'active'},
        'backgroundColor': 'rgba(0, 116, 217, 0.3)','border': '1px solid rgb(0, 116, 217)'
        }
    ]

#switch logic for greynoise <-> abuseipdb
@app.callback(
    [Output('remote_process_map', 'figure'),
    Output('processmaptable', 'data')],
    [Input('remote_map_toggle', 'value')])
def update_map_table(value):
    remote_process_map.gen_map(value)
    fig = remote_process_map.fig 
    tbl = remote_process_map.qresults
    data = tbl.to_dict('records')
    return [fig, data]