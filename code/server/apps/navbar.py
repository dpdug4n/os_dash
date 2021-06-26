import dash_bootstrap_components as dbc
def Navbar():
    navbar = dbc.NavbarSimple(
        children=[
            dbc.DropdownMenu(
                nav=True,
                in_navbar=True,
                label="Menu",
                children=[
                    dbc.DropdownMenuItem("Groups & Users", href='/apps/groups_users'),
                    dbc.DropdownMenuItem("Persistence", href='/apps/persistence'),
                    dbc.DropdownMenuItem("Remote Process Map", href="/apps/remote_process_map"),
                    dbc.DropdownMenuItem("Running Procceses", href='/apps/running_processes'),
                    dbc.DropdownMenuItem(divider=True),
                    dbc.DropdownMenuItem("Query Builder", href='/apps/query_builder'),
                    dbc.DropdownMenuItem(divider=True),
                    dbc.DropdownMenuItem("Settings", href='/apps/settings')
                ],
            ),
        ],
        brand="OSdash",
        brand_href="/home",
        sticky="top",
        )
    return navbar