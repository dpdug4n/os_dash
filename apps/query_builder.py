import dash, json
import dash_table
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd

from app import app
from apps.navbar import Navbar
from utils.inquire import host_queries 
from utils.maps_tables import query_table
nav = Navbar()
with open('assets\schema.json') as f:
    schema = json.load(f)

body = dbc.Container([
    dbc.Row(dbc.Col(html.H2("Query Builder"))),
    dbc.Row(dbc.Col(html.Div([
        html.H5("From:"),
        dcc.Dropdown(
            id = 'table-dropdown',
            options=[{'label': k, 'value': k} for k in schema.keys()],
        ),
        html.H5("Select:"),
        dcc.Dropdown(
            id = 'table-columns-dropdown',
            multi=True
        ),
        html.Hr(),
    ]))),
    
    dbc.Row(dbc.Col(html.Div([
        dcc.Textarea(
            id='query_input',
            style={'width':'100%', 'height':'200'},
            value="SELECT {columns} FROM {table}"
        ),
    html.Button('Ask your OS.', id='query_submit'),#add a link to scheme on far right column
    html.Div(id='query_table_container')]
    ))),
])

layout = html.Div([nav,body])

@app.callback(
    Output('table-columns-dropdown', 'options'),
    (Input('table-dropdown', 'value')))
def set_columns_dropdown(selected_table):
    if selected_table is None:
        return dash.no_update
    return [{'label': v, 'value': v} for v in schema[selected_table]]

@app.callback(
    Output('query_input', 'value'),
    [Input('table-dropdown','value'),
    Input('table-columns-dropdown', 'value'),
    State('query_input', 'value')])
def build_query(table, columns, current_input):
    #need to rethink this. won't update after first replace. 
    if table is None:
        return dash.no_update
    else:
        if columns is None:
            cols = '*'
        else: 
            cols = str(columns).replace("'",'').replace('[','').replace(']','')
        updated_input = "SELECT "+cols+" FROM "+table
        return updated_input


@app.callback(
    Output('query_table_container', 'children'),
    [Input('query_submit', 'n_clicks'),
    State('query_input', 'value')])
def update_query_table(value, n_clicks):
    return query_table(value, n_clicks)
