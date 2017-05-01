
import configparser
import json
import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

def test_ini():

    config = configparser.ConfigParser()
    config.sections()
    config.read('../config.ini')

    d = config._sections
    print(d)

def test_json():
    with open('../backtest.json', 'r') as f:
        data = json.load(f)
        print(data)

def test_yaml():
    with open('../backtest.yaml', 'r') as f:
        read_data = f.read()
        data = yaml.load(read_data)
        print(data)


test_ini()

test_json()

test_yaml()