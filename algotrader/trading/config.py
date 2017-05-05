import json
from typing import Dict

import yaml

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


class Config(object):
    def __init__(self, *configs: Dict):
        self.config = {}
        for config in configs:
            merge(config, self.config)

    def get(self, paths, default=None):
        result = self.config
        for path in paths.split("."):
            if path in result:
                result = result[path]
            else:
                return default

        return result

    def set(self, paths, value):
        result = self.config
        arr = paths.split(".")
        if len(arr) > 2:
            for path in arr[:-2]:
                if path in result:
                    result = result[path]
                else:
                    result[path] = {}
                    result = result[path]
            result[arr[-1]] = value
        else:
            result[paths] = value

    def get_app_config(self, path: str, default=None):
        return self.get("Application.%s" % path, default=default)

    def get_strategy_config(self, id: str, path: str, default=None):
        return self.get("Strategy.%s.%s" % (id, path), default=default)

    def get_feed_config(self, id: str, path: str, default=None):
        return self.get("Feed.%s.%s" % (id, path), default=default)

    def get_broker_config(self, id: str, path: str, default=None):
        return self.get("Broker.%s.%s" % (id, path), default=default)

    def get_datastore_config(self, id: str, path: str, default=None):
        return self.get("DataStore.%s.%s" % (id, path), default=default)


def merge(source: Dict, destination: Dict):
    for key, value in source.items():
        if isinstance(value, dict):
            node = destination.setdefault(key, {})
            merge(value, node)
        else:
            destination[key] = value


def save_to_json(path: str, config: Dict) -> None:
    with open(path, 'w') as f:
        json.dumps(config, f)


def save_to_yaml(path: str, config: Dict) -> None:
    with open(path, 'w') as f:
        yaml.dump(config, f, default_flow_style=False)


def load_from_json(path: str = '../../config/backtest.json') -> Dict:
    with open(path, 'r') as f:
        return json.load(f)


def load_from_yaml(path: str = '../../config/backtest.yaml') -> Dict:
    with open(path, 'r') as f:
        read_data = f.read()
        return yaml.load(read_data)
