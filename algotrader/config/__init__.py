import json

import yaml
from typing import Dict

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


class Config(object):
    def __init__(self, config: Dict):
        self.config = config

    def get(self, *args, default=None):
        result = self.config
        for arg in args:
            if arg in result:
                result = result[arg]
            else:
                return default

        return result

    def get_stg_config(self, stg_id, key, default=None):
        return self.get("Strategy", stg_id, key, default=default)


def load_from_json(path: str = 'backtest.json') -> Dict:
    with open(path, 'r') as f:
        return json.load(f)


def load_from_yaml(path: str = 'backtest.yaml') -> Dict:
    with open(path, 'r') as f:
        read_data = f.read()
        return yaml.load(read_data)
