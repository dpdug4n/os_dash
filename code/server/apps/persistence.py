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
from utils.maps_tables import auto_exec_table, chrome_extensions_table,firefox_addons_table,services_table, sc_tasks_table,startup_items_table

nav = Navbar()

body = dbc.Container([
    dbc.Row(dbc.Col(html.H2("Persistence"))),
    dbc.Row(dbc.Col(html.Div([
        dcc.Dropdown(
            id = 'table_selector',
            options=[
                {'label': 'AutoRun Executables', 'value':'autoexec'},
                {'label': 'Chromium-based Extensions', 'value':'chrome_extensions'},
                {'label': 'FireFox Addons', 'value':'firefox_addons'},
                {'label': 'Services', 'value':'services'},
                {'label': 'Scheduled Tasks', 'value':'sc_tasks'},
                {'label': 'Startup Items', 'value':'startup_items'},
            ],
            value = '',
            placeholder ='Select a table'
    ),html.Div(id='persistence_table_container')]
    ))),
])

layout = html.Div([nav,body])

@app.callback(
    Output('persistence_table_container', 'children'),
    [Input('table_selector', 'value')])
def update_output(value):
    if value == 'autoexec': return auto_exec_table(),
    elif value == 'chrome_extensions': return chrome_extensions_table(),
    elif value == 'firefox_addons': return firefox_addons_table(),
    elif value == 'services': return services_table(),
    elif value == 'sc_tasks': return sc_tasks_table(),
    elif value == 'startup_items': return startup_items_table()

