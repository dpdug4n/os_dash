# OSdash
OSdash is an open-source project for visualizing the exploration and monitoring of your operating system. Please note that this is not built for production environments and is for educational purposes. Built for Windows 10.    

## Setup  
* Install [python](https://www.python.org/) and [osquery](https://osquery.io/), then create accounts at [abuseipdb](https://www.abuseipdb.com/), [greynoise](https://developer.greynoise.io/docs/using-the-greynoise-community-api) and [maxmind](https://dev.maxmind.com/geoip/geoip2/geolite2/).  

* Download this repo: ```git clone  https://github.com/dpdug4n/os_dash```

* ``cd os_dash``
* ``pip install -r requirements.txt``

* Download maxmind's geolite2-city database and save it in ```\assets```.

* You will need to set your API keys as system variables.  
Press ``Win+R`` then enter ``rundll32 sysdm.cpl,EditEnvironmentVariables
`` to bring up the menu.  
Create two new user variables named ``abuseipdb_key`` and ``greynoise_key`` with the respective API keys for the values. 

## Run
* ``python index.py``
* Navigate [here](http://127.0.0.1:8050/home) in your preferred browser.


