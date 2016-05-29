import datetime

import msgpack

from algotrader.utils import msgpack_numpy as m

m.patch()
from algotrader.event.market_data import MarketDataEvent

import importlib

cache = {}

def decode(obj):
    if b'__datetime__' in obj:
        obj = datetime.datetime.strptime(obj["as_str"], "%Y%m%dT%H:%M:%S.%f")
    elif b'cls' in obj:
        data = obj
        module = obj[b'module']
        cls = obj[b'cls']
        if (module, cls) not in cache:
            m = importlib.import_module(module)
            c = getattr(m, cls)
            cache[(module, cls)] = c
        c = cache[(module, cls)]
        obj = c()
        obj.deserialize(data)
    return obj

def encode(obj):
    if isinstance(obj, MarketDataEvent):
        return obj.serialize()
    if isinstance(obj, datetime.datetime):
        return {'__datetime__': True, 'as_str': obj.strftime("%Y%m%dT%H:%M:%S.%f")}

    return obj

items = [bar, quote, trade]

for item in items:
    packed_dict = msgpack.packb(item, default=encode)
    item2 = msgpack.unpackb(packed_dict, object_hook=decode)
    print item
    print item2