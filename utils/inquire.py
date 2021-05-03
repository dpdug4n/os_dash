import sys, osquery, geoip2.database, requests, ipaddress, json, os
import pandas as pd
from requests import get
from greynoise import GreyNoise


class host_queries():

    book = {
            'remoteProcessConnections':  "SELECT DISTINCT s.pid, p.name, local_address, remote_address, local_port, remote_port FROM process_open_sockets s JOIN processes p ON s.pid = p.pid WHERE remote_address NOT IN ('127.0.0.1', '169.254.169.254', '', '0000:0000:0000:0000:0000:0000:0000:0001','0','::', '::1', '0000:0000:0000:0000:0000:ffff:7f00:0001', 'unknown', '0.0.0.0', '0000:0000:0000:0000:0000:0000:0000:0000') AND remote_address NOT LIKE '192.168%' AND remote_address NOT LIKE '172.16%' AND remote_address NOT LIKE '10%'",
            'running_processes':"SELECT start_time, name, pid, cmdline, path, state, cwd, on_disk from processes ORDER BY start_time DESC",
            'sc_tasks':'SELECT name, action, path, enabled, hidden, last_run_time, next_run_time FROM scheduled_tasks',
            'services': "SELECT name, display_name,user_account,path FROM services WHERE path NOT LIKE 'C:\Windows\system32\svchost.exe -k %'",
            'startup_items':"SELECT name, path, args, username FROM startup_items WHERE name NOT LIKE 'desktop.ini'",
            'autoexec':'SELECT * FROM autoexec',
            'chrome_extensions':'SELECT u.username, extensions.name, extensions.identifier,extensions.version,extensions.permissions,extensions.optional_permissions FROM users u CROSS JOIN chrome_extensions extensions USING (uid)',
            'firefox_addons':'SELECT u.username, extensions.name, extensions.identifier,extensions.version,extensions.description,extensions.source_url FROM users u CROSS JOIN firefox_addons extensions USING (uid)'
        }
        
    def query(q):
        #https://github.com/osquery/osquery-python/blob/master/examples/spawn.py
        INSTANCE = osquery.SpawnInstance(os.getenv('osquery_socket','C:/Program Files/osquery/osqueryd/osqueryd.exe'))
        INSTANCE.open()
        RESULTS = INSTANCE.client.query(q)
        INSTANCE.connection=None
        if RESULTS.status.code != 0:
            print("Error running the query: %s" % RESULTS.status.message)
            host_queries.queryresults = pd.DataFrame()
            host_queries.query_error = str("Error running the query: %s" % RESULTS.status.message)
            return 
        else:
            data = RESULTS.response
            host_queries.queryresults = pd.DataFrame(data)
    
    def pidtree(pid):
        q = "WITH RECURSIVE rc(pid, parent, name) AS (SELECT pid, parent, name FROM processes WHERE pid = PROCESSID UNION ALL SELECT p.pid, p.parent, p.name FROM processes AS p, rc WHERE p.pid = rc.parent AND p.pid != 0) SELECT pid, parent, name FROM rc LIMIT 20"
        q = q.replace('PROCESSID', pid)
        host_queries.query(q)
        host_queries.pidtreeresults = host_queries.queryresults

class utils():
    def geoIP(IPlist):
        #https://github.com/maxmind/GeoIP2-python
        utils.rIPlat =[]
        utils.rIPlon = []
        utils.srcIPlat = []
        utils.srcIPlon = []
        srcIP = get('https://api.ipify.org').text
        with geoip2.database.Reader(os.getenv('geolite2_city_db','assets/GeoLite2-City.mmdb')) as reader: 
            for rIP in IPlist:
                try:
                    response = reader.city(rIP)
                    utils.rIPlat.append(response.location.latitude)
                    utils.rIPlon.append(response.location.longitude)
                    srcResponse = reader.city(srcIP)
                    utils.srcIPlat.append(srcResponse.location.latitude)
                    utils.srcIPlon.append(srcResponse.location.longitude)
                except Exception as e:
                    utils.rIPlat.append(0)
                    utils.rIPlon.append(0)
                    srcResponse = reader.city(srcIP)
                    utils.srcIPlat.append(srcResponse.location.latitude)
                    utils.srcIPlon.append(srcResponse.location.longitude)
                    
    def abuseIPCheck(rIP):
        #https://www.abuseipdb.com/api.html
        api_key = os.getenv('abuseipdb_key')
        utils.rIPRating =[]
        utils.rIPDomain = []
        for ip in rIP:
            if ipaddress.ip_address(ip).is_private is False:
                headers = {
                    'Key': api_key,
                    'Accept': 'application/json',
                }
                params = {
                    'ipAddress': ip,
                    'maxAgeInDays': '30',
                }
                r = requests.get('https://api.abuseipdb.com/api/v2/check',
                                headers=headers, params=params)
                response = r.json()
                if 'errors' in response:
                    utils.rIPRating.append('error')
                    utils.rIPDomain.append(response['data']['domain'])
                elif response['data']['abuseConfidenceScore'] in range(80,101):
                    utils.rIPRating.append('High')
                    utils.rIPDomain.append(response['data']['domain'])
                elif response['data']['abuseConfidenceScore'] in range(30,79):
                    utils.rIPRating.append('Medium')
                    utils.rIPDomain.append(response['data']['domain'])
                #elif response['data']['abuseConfidenceScore'] in range(0,29):
                else:
                    utils.rIPRating.append('Low')
                    utils.rIPDomain.append(response['data']['domain'])   
            else:
                utils.rIPRating.append('Private')
                utils.rIPDomain.append('Local')

    def gnIPCheck(rIP):
        #https://developer.greynoise.io/docs/using-the-greynoise-community-api
        api_key = os.getenv('greynoise_key')
        api_client = GreyNoise(api_key=api_key)
        utils.rIPRating =[]
        utils.rIPDomain = []
        for ip in rIP:
            if ipaddress.ip_address(ip).is_private is False:
                response = api_client.ip(ip)
                if response['seen'] is False:
                    utils.rIPRating.append('unknown')
                    utils.rIPDomain.append('unknown')
                elif response['classification'] == 'malicious':
                    utils.rIPRating.append('High')
                    utils.rIPDomain.append(response['metadata']['organization'])
                elif response['classification'] == 'unknown':
                    utils.rIPRating.append('Medium')
                    utils.rIPDomain.append(response['metadata']['organization'])
                elif response['classification'] == 'benign':
                    utils.rIPRating.append('Low')
                    utils.rIPDomain.append(response['metadata']['organization'])
                else:
                    utils.rIPRating.append('error')
                    utils.rIPDomain.append('error')
            else:
                utils.rIPRating.append('Private')
                utils.rIPDomain.append('Local')

