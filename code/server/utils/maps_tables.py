import pandas as pd
import dash_table, dash, traceback
import plotly.graph_objects as go
from datetime import datetime
from utils.inquire import host_queries, utils

def epoch_to_local(timestamp):
    try:
        local_datetime_converted = datetime.fromtimestamp(int(timestamp)).strftime('%m-%d-%Y %H:%M')
        return local_datetime_converted
    except:
        return timestamp


class remote_process_map():
    def __init__(self):
        pass
    def gen_map(self, toggle_val=False):
        fig = go.FigureWidget()
        qresults = pd.DataFrame()
        host_queries.query(host_queries.book['remoteProcessConnections'])
        try:
            #GeoIP Lookup
            #This product includes GeoLite2 data created by MaxMind, available from
            #<a href="https://www.maxmind.com">https://www.maxmind.com</a>.
            try:
                utils.geoIP(host_queries.queryresults.remote_address.to_list())
                qresults = host_queries.queryresults.assign(Latitude = utils.rIPlat, Longitude = utils.rIPlon, srcLatitude = utils.srcIPlat, srcLongitude = utils.srcIPlon)
            except:
                traceback.print_exc()
                pass
            #GreyNoise IP Check. Unlimited with account but less info.
            if toggle_val is  False:
                try:
                    utils.gnIPCheck(qresults.remote_address.to_list())
                    qresults = qresults.assign(Abuse_Rating= utils.rIPRating, Domain = utils.rIPDomain)
                except:
                    traceback.print_exc()
            # #AbuseIPDB check. Rate limited but more info/larger db. Should make toggle option in settings to switch between these
            if toggle_val is True:
                try:
                    utils.abuseIPCheck(qresults.remote_address.to_list())
                    qresults = qresults.assign(Abuse_Rating= utils.rIPRating, Domain = utils.rIPDomain)
                except:
                    traceback.print_exc()
                    pass
        except:
            qresults = qresults.assign(Abuse_Rating= "", Domain = "")
        
        try:
            #add lines from src to dst
            for i in range(len(qresults)):
                if qresults['Abuse_Rating'][i] == 'High':
                    fig.add_trace(
                        go.Scattergeo(
                            name = qresults['name'][i],
                            lat = (qresults['srcLatitude'][i], qresults['Latitude'][i]),
                            lon = (qresults['srcLongitude'][i], qresults['Longitude'][i]),
                            mode = 'lines',
                            line = dict(width = 2, color = 'red'),
                            opacity = 0.45,
                            showlegend = False
                        )
                    )
                if qresults['Abuse_Rating'][i] == 'Medium':
                    fig.add_trace(
                        go.Scattergeo(
                            name = qresults['name'][i],
                            lat = (qresults['srcLatitude'][i], qresults['Latitude'][i]),
                            lon = (qresults['srcLongitude'][i], qresults['Longitude'][i]),
                            mode = 'lines',
                            line = dict(width = 2, color = 'yellow'),
                            opacity = 0.45,
                            showlegend = False
                        )
                    )
                if qresults['Abuse_Rating'][i] == 'Low':
                    fig.add_trace(
                        go.Scattergeo(
                            name = qresults['name'][i],
                            lat = (qresults['srcLatitude'][i], qresults['Latitude'][i]),
                            lon = (qresults['srcLongitude'][i], qresults['Longitude'][i]),
                            mode = 'lines',
                            line = dict(width = 2, color = 'green'),
                            opacity = 0.45,
                            showlegend = False
                        )
                    )
                if qresults['Abuse_Rating'][i] == 'unknown':
                    fig.add_trace(
                        go.Scattergeo(
                            name = qresults['name'][i],
                            lat = (qresults['srcLatitude'][i], qresults['Latitude'][i]),
                            lon = (qresults['srcLongitude'][i], qresults['Longitude'][i]),
                            mode = 'lines',
                            line = dict(width = 2, color = 'grey'),
                            opacity = 0.45,
                            showlegend = False
                        )
                    )
            #plot src & dst
            for i in range(len(qresults)):
                fig.add_trace(
                    go.Scattergeo(
                        name = qresults['name'][i],
                        lat = (qresults['srcLatitude'][i], qresults['Latitude'][i]),
                        lon = (qresults['srcLongitude'][i], qresults['Longitude'][i]),
                        hoverinfo = 'text',
                        text = str("Process : "+ qresults['name'][i] +"<br>ProcessID: "+ qresults['pid'][i] +"<br>Local Port: "+qresults['local_port'][i] +"<br>Domain: "+ qresults['Domain'][i] +"<br>RemoteAddress: "+ qresults['remote_address'][i] +"<br>RemotePort: "+ qresults['remote_port'][i]),
                        mode = 'markers',
                        marker = dict(size = 10, color = 'blue', opacity = 0.5)
                    )
                )
            #update layout for styling
            fig.update_geos(
                resolution=50,
                showcountries=True, countrycolor='rgb(18, 242, 246)',
                landcolor ='rgb(0, 9, 9)', lakecolor = 'rgb(10, 9, 87)',
                showocean = True, oceancolor = 'rgb(10, 9, 87)',
                showcoastlines=True, coastlinecolor='rgb(18, 242, 246)'
            )
            fig.update_layout(
                title_text = 'Host Network Connections',
                height = 500, width = 1000,
                margin={"t":0,"b":0,"l":0, "r":0, "pad":0},
                showlegend=True,
                geo= dict(projection_type = 'equirectangular', showland = True),
                clickmode='event+select'
            )
            self.fig = fig
            self.qresults = qresults
            return self.fig, self.qresults
        #return empty fig & partial table if API checks fail
        except:
            traceback.print_exc()
            self.fig = fig
            self.qresults = qresults
            return self.fig, self.qresults

class running_processes():
    def __init__(self, fig, qresults):
        self.fig = fig
        self.qresults = qresults
    try:
        host_queries.query(host_queries.book['running_processes'])
        qresults = host_queries.queryresults
        qresults = qresults[['start_time', 'name', 'pid', 'cmdline', 'path','cwd', 'state', 'on_disk']]
        qresults['start_time'] = qresults['start_time'].apply(epoch_to_local)
        #set on disk to True or False, clean IS_ACTIVE
        def on_disk_reformat(value):
            try:
                if value == '1':
                    return 'True'
                elif value == '0':
                    return 'False'
                else:
                    return value 
            except Exception:
                print(Exception)
        qresults['on_disk'] = qresults['on_disk'].apply(on_disk_reformat)
    except:
        traceback.print_exc()

def auto_exec_table():
    host_queries.query(host_queries.book['autoexec'])
    autoexec_df = host_queries.queryresults
    autoexec_ColNames = ['Name','Path','Source']
    if autoexec_df.empty:
        return "No results"
    autoexec = dash_table.DataTable( 
        id='autoexec_table',
        columns=[{"name": x, "id": y} for x,y in zip(autoexec_ColNames,autoexec_df.columns)],
        data=autoexec_df.to_dict('records'),
        filter_action='native',
        sort_mode = 'multi',
        sort_action='native',
        row_deletable=True,
        fixed_rows={'headers':True},
        style_table={'overflowX': 'scroll'},
        style_cell={
            'textAlign': 'left', 
            'maxWidth':400,
            'minWidth':80
                        },)
    return autoexec

def chrome_extensions_table():
    host_queries.query(host_queries.book['chrome_extensions'])
    chrome_extensions_df = host_queries.queryresults
    if chrome_extensions_df.empty:
        return "No results"
    chrome_extensions_df = chrome_extensions_df[['username','name','permissions','optional_permissions','identifier','version']]
    chrome_extensions = dash_table.DataTable( 
        id='chrome_extensions_table',
        columns=[{"name": x, "id": x} for x in chrome_extensions_df.columns],
        data=chrome_extensions_df.to_dict('records'),
        filter_action='native',
        sort_mode = 'multi',
        sort_action='native',
        row_deletable=True,
        fixed_rows={'headers':True},
        style_table={'overflowX': 'scroll'},
        style_cell={
            'textAlign': 'left', 
            'minWidth':175
                        },)
    return chrome_extensions

def firefox_addons_table():
    host_queries.query(host_queries.book['firefox_addons'])
    firefox_addons_df = host_queries.queryresults
    if firefox_addons_df.empty:
        return "No results"
    firefox_addons = dash_table.DataTable( 
        id='firefox_addons_table',
        columns=[{"name": x, "id": x} for x in firefox_addons_df.columns],
        data=firefox_addons_df.to_dict('records'),
        filter_action='native',
        sort_mode = 'multi',
        sort_action='native',
        row_deletable=True,
        fixed_rows={'headers':True},

        style_table={'overflowX': 'scroll'},
        style_cell={
            'textAlign': 'left', 
            'maxWidth':400,
            'minWidth':80
                        },)
    return firefox_addons

def services_table():
    host_queries.query(host_queries.book['services'])
    services_df = host_queries.queryresults
    if services_df.empty:
        return "No results"
    services = dash_table.DataTable( 
        id='services_table',
        columns=[{"name": x, "id": x} for x in services_df.columns],
        data=services_df.to_dict('records'),
        filter_action='native',
        sort_mode = 'multi',
        sort_action='native',
        row_deletable=True,
        fixed_rows={'headers':True},
        style_table={'overflowX': 'scroll'},
        style_cell={
            'textAlign': 'left', 
            'maxWidth':400,
            'minWidth':80
                        },)
    return services

def sc_tasks_table():
    host_queries.query(host_queries.book['sc_tasks'])
    sc_tasks_df = host_queries.queryresults
    if sc_tasks_df.empty:
        return "No results"
    sc_tasks_df['last_run_time'] = sc_tasks_df['last_run_time'].apply(epoch_to_local)
    sc_tasks_df['next_run_time'] = sc_tasks_df['next_run_time'].apply(epoch_to_local)
    sc_tasks_df = sc_tasks_df[['enabled','name', 'action', 'last_run_time','next_run_time','path','hidden']]
    sc_tasks = dash_table.DataTable( 
        id='sc_tasks_table',
        columns=[{"name": x, "id": x} for x in sc_tasks_df.columns],
        data=sc_tasks_df.to_dict('records'),
        filter_action='native',
        sort_mode = 'multi',
        sort_action='native',
        row_deletable=True,
        fixed_rows={'headers':True},
        style_table={'overflowX': 'scroll'},
        style_cell={
            'textAlign': 'left', 
            'minWidth':65
                        },)
    return sc_tasks

def startup_items_table():
    host_queries.query(host_queries.book['startup_items'])
    startup_items_df = host_queries.queryresults
    if startup_items_df.empty:
        return "No results"
    startup_items_df =startup_items_df[['username','name','path','args']]
    startup_items = dash_table.DataTable( 
        id='startup_items_table',
        columns=[{"name": x, "id": x} for x in startup_items_df.columns],
        data=startup_items_df.to_dict('records'),
        filter_action='native',
        sort_mode = 'multi',
        sort_action='native',
        row_deletable=True,
        fixed_rows={'headers':True},
        style_table={'overflowX': 'scroll'},
        style_cell={
            'textAlign': 'left', 
            'minWidth':80
                        },)
    return startup_items

def query_table(n_clicks, value):
    if n_clicks is None:
        return dash.no_update
    host_queries.query(str(value))
    query_results = host_queries.queryresults
    if query_results.empty: 
        return host_queries.query_error 
    query_table = dash_table.DataTable( 
        id='query_table',
        columns=[{"name": x, "id": x} for x in query_results.columns],
        data=query_results.to_dict('records'),
        filter_action='native',
        sort_mode = 'multi',
        sort_action='native',
        row_deletable=True,
        fixed_rows={'headers':True},
        style_table={'overflowX': 'scroll'},
        style_cell={
            'textAlign': 'left', 
            'minWidth':175
                        },)
    return query_table