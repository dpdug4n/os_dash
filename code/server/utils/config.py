import json

def get(key):
        with open('utils/config.json', 'r') as c:
            config = json.load(c)
        return config[key]

def write(key,value):
        with open('utils/config.json', 'r') as c:
            config = json.load(c)
        with open('utils/config.json', 'w') as c:
            config[key] = value
            print(config)
            json.dump(config, c)
            print(config)