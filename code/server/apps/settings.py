import dash, os, json
import utils.config as config
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
                        html.H3("Client Configuration",),
                        dbc.Label("OS Type:", html_for="os_type"),
                        dcc.Dropdown(
                            id='os_type',
                            options = [{'label': os , 'value': os} for os in ['Windows', 'macOS','Linux']],
                            value = config.get('client_os'),
                            clearable=False,
                        ),
                        dbc.Label("Client Address:", html_for="client_address"),
                        dbc.Input(id="client_address", value=config.get("client_address")),
                        dbc.Label("Client Port:", html_for="client_port"),
                        dbc.Input(id="client_port", value=config.get("client_port")),
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
                        dbc.Input(id="gl2cdb", value=config.get("maxmind_geolite2_city_db")),
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
                        dbc.Input(id="abuseipdb_key", value=config.get("abuse_ipdb_api_key")),
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
                        dbc.Input(id="greynoise_key", value=config.get("grey_noise_api_key")),
                    ]
                ),
            ),
            form = True,
        ),
        dbc.Row(
            dbc.Col(
                dbc.FormGroup(
                    [
                        dbc.Label("Theme:", html_for="themes"),
                        dcc.Dropdown(
                            id = 'themes',
                            options=[{'label': theme , 'value': theme} for theme in dir(dbc.themes) if not theme.startswith('__')],
                            value = config.get("theme"),
                            clearable=False,
                        ),
                        
                    ]
                ),
            ),
            form = True,
        ),
        html.Div(id='placeholder', style={'display':'none'})
    ]
)


layout = html.Div([
    nav,
    body,
    
])

@app.callback(
    [#Output("save_output", "children"),
    Output("os_type", "value"),
    Output("client_address", "value"),
    Output("client_port", "value"),
    Output("gl2cdb", "value"),
    Output("abuseipdb_key", "value"),
    Output("greynoise_key", "value"),
    Output("themes", "value")],
    [Input("save_button", "n_clicks"),
    Input("themes", "value"),
    State("os_type", "value"),
    State("client_address", "value"),
    State("client_port", "value"),
    State("gl2cdb", "value"),
    State("abuseipdb_key", "value"),
    State("greynoise_key", "value"),
 ]
)
def on_button_click(n,theme,os,c_a,c_p,gl2,ak,gk,):
    if n is None:
        return dash.no_update
    else:
        new_config =[]
        new_config.append(['client_os', os])
        new_config.append(['client_address', c_a])
        new_config.append(['client_port', c_p])
        new_config.append(["maxmind_geolite2_city_db", gl2])
        new_config.append(["abuse_ipdb_api_key", ak])
        new_config.append(["grey_noise_api_key", gk])
        new_config.append(["theme", theme])
        [config.write(key, value) for key, value in new_config]
        return os, c_a, c_p, gl2, ak, gk, theme
        

app.clientside_callback(
    #https://community.plotly.com/t/dash-bootstrap-theme-switcher/50798/2
    """
    function(theme) {
        var stylesheet = document.querySelector('link[rel=stylesheet][href^="https://stackpath"]')
        var name = theme.toLowerCase()
        if (name === 'bootstrap') {
            var link = 'https://stackpath.bootstrapcdn.com/bootstrap/4.5.0/css/bootstrap.min.css'
          } else {
            var link = "https://stackpath.bootstrapcdn.com/bootswatch/4.5.0/" + name + "/bootstrap.min.css"
        }
        stylesheet.href = link
    }
    """,
    Output("placeholder", "children"),
    Input("themes", "value"),
)
