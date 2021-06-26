# OSdash
OSdash is an open-source project for visualizing the exploration and monitoring of operating systems. Please note that this is not built for production environments and is for educational purposes. Use at your own risk.   

## Setup  
<sub><sup>This is presuming the client & server are on the same local/virtual network. You can add ``"bridge": "bridge_name",`` to [/etc/docker/daemon.json](https://docs.docker.com/engine/reference/commandline/dockerd/) to change the default docker bridge.<sup></sub>
### Host 
* Install [python](https://www.python.org/) and [osquery](https://osquery.io/) on the host to monitor, then create accounts at [abuseipdb](https://www.abuseipdb.com/), [greynoise](https://developer.greynoise.io/docs/using-the-greynoise-community-api) and [maxmind](https://dev.maxmind.com/geoip/geoip2/geolite2/).  

* Download and run client_shell.py: ``pip install requests && curl {url} > client_shell.py && python client_shell.py``
### Server
* Download this repo: ``git clone -branch osdash_docker https://github.com/dpdug4n/os_dash``
* ``cd os_dash\code\server``
* Download maxmind's geolite2-city database and save it in ``\assets``.
* Settings page isn't 100% functional yet, save your API keys, host details, etc in ``\utils\config.json``
* ``docker build . -t server``  
* ``docker run --rm -it -p 8050:8050 --name os_dash server``
* Navigate to http://localhost:8050/ 

# Demo
![Demo](https://user-images.githubusercontent.com/33767549/119290788-3b4d6980-bc1b-11eb-95fd-00bd9930eae6.gif)
