from ourdomain import OurDomain
from config import Config
import json
from time import sleep

def load_config():
    with open('config.json', 'r', encoding='utf-8') as config_file:
        config = json.load(config_file)
    return Config(**config
                  )

config = load_config()
od = OurDomain(config)
od.login()
index_bool = od.floor_plan()
while (True):
    sleep(0.01)
    index_bool = od.index()
    if index_bool:
        break