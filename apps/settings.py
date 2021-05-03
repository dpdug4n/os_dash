import dash, os
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from app import app
from apps.navbar import Navbar

nav = Navbar()

body = dbc.Container(
    [
        dbc.Row([
            dbc.Col([
                html.H2("Settings"),
                html.Span(id="save_output", style={"vertical-align": "middle"}),
            ]),
            dbc.Col(
                dbc.Button("Save", id='save_button', color='primary'), width={"offest":7},
                )
            ],
            justify="around"
        ),
        dbc.Row(
            dbc.Col(
                dbc.FormGroup(
                    [
                        dbc.Label("OSquery Socket:", html_for="osquery_socket"),
                        dbc.Input(id="osquery_socket", placeholder=os.getenv('osquery_socket','C:/Program Files/osquery/osqueryd/osqueryd.exe')),
                    ]
                ),
            ),
            form = True
        ),
                dbc.Row(
            dbc.Col(
                dbc.FormGroup(
                    [
                        dbc.Label("MaxMind GeoLite2 City DataBase:", html_for="gl2cdb"),
                        dbc.Input(id="gl2cdb", placeholder=os.getenv('geolite2_city_db','assets/GeoLite2-City.mmdb')),
                    ]
                ),
            ),
            form = True,
        ),
        dbc.Row(
            dbc.Col(
                dbc.FormGroup(
                    [
                        dbc.Label("AbuseIPDB API Key:", html_for="abuseipdb_key"),
                        dbc.Input(id="abuseipdb_key", placeholder=os.getenv('abuseipdb_key')),
                    ]
                ),
            ),
            form = True
        ),
        dbc.Row(
            dbc.Col(
                dbc.FormGroup(
                    [
                        dbc.Label("GreyNoise API Key:", html_for="greynoise_key"),
                        dbc.Input(id="greynoise_key", placeholder=os.getenv('greynoise_key')),
                    ]
                ),
            ),
            form = True,
        ),

    ]
)


layout = html.Div([
    nav,
    body
])

@app.callback(
    [Output("save_output", "children"),
    Output("osquery_socket", "value"),
    Output("gl2cdb", "value"),
    Output("abuseipdb_key", "value"),
    Output("greynoise_key", "value")],
    [Input("save_button", "n_clicks"),
    State("osquery_socket", "value"),
    State("gl2cdb", "value"),
    State("abuseipdb_key", "value"),
    State("greynoise_key", "value")]
)
def on_button_click(n,osq,gl2,ak,gk):
    if n is None:
        return dash.no_update
    elif osq is not None:
        os.environ['osquery_socket'] = osq
    elif gl2 is not None:
        os.environ['geolite2_city_db'] = gl2
    elif ak is not None:
        os.environ['abuseipdb_key'] = ak
    elif gk is not None:
        os.environ['greynoise_key'] = gk        
    return n, osq, gl2, ak, gk
    #need to switch this to config file, or use subprocess to updated registry keys. Former is preferred, latter is unsafe.