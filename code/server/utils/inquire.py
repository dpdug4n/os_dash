import osquery, geoip2.database, requests, ipaddress, socket, pickle, traceback
import pandas as pd
from requests import get
from greynoise import GreyNoise
import utils.config as config

class host_queries():
    def __init__(self):
        pass
    
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
    macBook={}
    linuxBook={}
    
    def query(q):
        client_address =config.get("client_address")
        client_port = config.get("client_port")
        host_queries.queryresults = pd.DataFrame()
        host_queries.query_error = 'Error. The column may not exist on the host.'
        def pull_query_results(client_address, client_port, query):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((client_address,client_port))
            reply = s.recv(4).decode()
            if reply == 'true':
                print(f'Connected to {client_address}:{client_port}')
            else:
                print(f'Error. Disconnected from {client_address}:{client_port}')
                s.close
                return 
            #need to recieve public IP here
            packet_size = s.recv(4096).decode()
            utils.srcIP = packet_size
            s.send(query.encode())
            packet_size = s.recv(4096).decode()
            print(f'{packet_size} bytes to receive \n')
            s.send("10-4".encode())
            data = []
            recieved_packet_size = 0
            while True:
                packet = s.recv(4096)
                if not packet: break
                recieved_packet_size += len(packet)
                data.append(packet)
            if str(recieved_packet_size) != str(packet_size):
                print(f'Error:{recieved_packet_size} bytes received. \n')
                print(f'Disconnected from {client_address}:{client_port}')
                s.close()
            else:      
                results = pickle.loads(b"".join(data))
                print(f'{recieved_packet_size} bytes received. \n')
                print(f'Disconnected from {client_address}:{client_port}')
                s.close()
            try:
                results = pd.DataFrame(results)
                return results
            except:
                # This decode returns a 'V' & 'p0', at the beginning/end of string & [1:-2] doesnt work
                # research later, fix below yields same results
                error = pickle.dumps(results, 0).decode('utf-8')[1:]
                error = error.replace('p0','')
                host_queries.query_error = error
                results = pd.DataFrame()
                return results
        try:    
            host_queries.queryresults = pull_query_results(client_address,client_port,q)
        except:
            traceback.print_exc()

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
        srcIP = utils.srcIP
        with geoip2.database.Reader(config.get('maxmind_geolite2_city_db')) as reader: 
            for rIP in IPlist:
                try:
                    response = reader.city(rIP)
                    utils.rIPlat.append(response.location.latitude)
                    utils.rIPlon.append(response.location.longitude)
                    srcResponse = reader.city(srcIP)
                    utils.srcIPlat.append(srcResponse.location.latitude)
                    utils.srcIPlon.append(srcResponse.location.longitude)
                except:
                    utils.rIPlat.append(0)
                    utils.rIPlon.append(0)
                    srcResponse = reader.city(srcIP)
                    utils.srcIPlat.append(srcResponse.location.latitude)
                    utils.srcIPlon.append(srcResponse.location.longitude)
                    
    def abuseIPCheck(rIP):
        #https://www.abuseipdb.com/api.html
        api_key = config.get('abuse_ipdb_api_key')
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
        api_key = config.get('grey_noise_api_key')
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

