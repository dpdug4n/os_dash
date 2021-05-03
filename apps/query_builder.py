import dash
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

body = dbc.Container([
    dbc.Row(dbc.Col(html.H2("Query Builder"))),
    dbc.Row(dbc.Col(html.Div([
        dcc.Textarea(
            id='query_input',
            style={'width':'100%', 'height':'200'}
        ),
    html.Button('Ask your OS.', id='query_submit'),#add a link to scheme on far right column
    html.Div(id='query_table_container')]
    ))),
])

layout = html.Div([nav,body])

@app.callback(
    Output('query_table_container', 'children'),
    [Input('query_submit', 'n_clicks'),
    State('query_input', 'value')])
def update_query_table(value, n_clicks):
    return query_table(value, n_clicks)
