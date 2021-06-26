import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html

from apps.navbar import Navbar

nav = Navbar()

body = dbc.Container([
    dbc.Row(dbc.Col(
                dcc.Markdown('''
                            ### About the project:  
                            OSDash is an open-source project for visualizing the exploration and monitoring of your operating system.
                            This project currently relies on osquery, Plotly Dash, AbuseIPDB, GreyNoise, and MaxMind's GeoLite2.
                '''))
    )
])

layout = html.Div([
    nav,
    body
])


