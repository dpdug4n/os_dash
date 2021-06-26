import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from apps import home, settings, groups_users, remote_process_map, running_processes, persistence, query_builder


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])


@app.callback(Output('page-content', 'children'),
                Input('url', 'pathname'))
def display_page(pathname='/home'):
    if pathname == '/home':
        return home.layout
    elif pathname == '/apps/settings':
        return settings.layout
    elif pathname == '/apps/remote_process_map':
        return remote_process_map.layout
    elif pathname == '/apps/running_processes':
        return running_processes.layout
    elif pathname == '/apps/persistence':
        return persistence.layout
    elif pathname == '/apps/groups_users':
        return groups_users.layout   
    elif pathname == '/apps/query_builder':
        return query_builder.layout     
    else:
        return home.layout

if __name__ == '__main__':
    app.run_server(host='0.0.0.0',debug=True)