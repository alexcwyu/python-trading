import datetime

from algotrader.utils import msgpack_numpy as m

m.patch()
import importlib
import msgpack
import abc
import json
from itertools import chain


class Serializable(object):
    def serialize(self):
        map = {}
        map['@p'] = self.__module__
        map['@t'] = self.__class__.__name__
        map['__slots__'] = self.__data__()
        map['__dict__'] = self.__dict__
        return map

    def deserialize(self, map):
        if '__slots__' in map:
            data = map['__slots__']
            for k, v in data.items():
                setattr(self, k, v)
        if '__dict__' in map:
            data = map['__dict__']
            for k, v in data.items():
                self.__dict__[k] = v

    def __data__(self):
        attr_list = []
        for cls in self.__class__.__mro__:
            attrs = getattr(cls, '__slots__', [])
            if isinstance(attrs, (list, tuple)):
                attr_list.append(attrs)
            else:
                attr_list.append([attrs])
        return {s: getattr(self, s) for s in chain.from_iterable(attr_list) if hasattr(self, s)}

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
                and self.__data__() == other.__data__() and self.__dict__ == other.__dict__)

    def __ne__(self, other):
        return not self.__eq__(other)


class TradeData(Serializable):
    pass


class Serializer(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def serialize(self, obj):
        raise NotImplementedError()

    @abc.abstractmethod
    def deserialize(self, data):
        raise NotImplementedError()


cls_cache = {}


def decode(obj):
    if b'__datetime__' in obj:
        obj = datetime.datetime.strptime(obj["__datetime__"], "%Y%m%dT%H:%M:%S.%f")
    elif b'@t' in obj:
        data = obj
        module = obj[b'@p']
        cls = obj[b'@t']
        if (module, cls) not in cls_cache:
            m = importlib.import_module(module)
            c = getattr(m, cls)
            cls_cache[(module, cls)] = c
        c = cls_cache[(module, cls)]
        obj = c()
        obj.deserialize(data)
    return obj


def encode(obj):
    if isinstance(obj, Serializable):
        return obj.serialize()
    if isinstance(obj, datetime.datetime):
        return {'__datetime__': obj.strftime("%Y%m%dT%H:%M:%S.%f")}

    return obj


class MsgPackSerializer(Serializer):
    def serialize(self, obj):
        return msgpack.packb(obj, default=encode)

    def deserialize(self, data):
        return msgpack.unpackb(data, object_hook=decode)


class JsonSerializer(Serializer):
    def serialize(self, obj):
        return json.dumps(obj, default=encode)

    def deserialize(self, data):
        return json.loads(data, object_hook=decode)
