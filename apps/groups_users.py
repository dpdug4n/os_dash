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

nav = Navbar()

body = dbc.Container([
    dbc.Row(dbc.Col(html.H2("Groups and Users"))),
    dbc.Row(dbc.Col(html.Div([

    
    ]))),
])

layout = html.Div([nav,body])