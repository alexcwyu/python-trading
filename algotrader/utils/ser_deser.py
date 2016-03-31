import datetime

from algotrader.utils import msgpack_numpy as m

m.patch()
import importlib
import msgpack
import abc

from itertools import chain


class Serializable(object):
    def serialize(self):
        map = {}
        map['module'] = self.__module__
        map['cls'] = self.__class__.__name__
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
        return {s: getattr(self, s) for s in
                chain.from_iterable(getattr(cls, '__slots__', []) for cls in self.__class__.__mro__) if
                hasattr(self, s)}

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
                and self.__data__() == other.__data__() and self.__dict__ == other.__dict__)

    def __ne__(self, other):
        return not self.__eq__(other)


class Serializer(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def serialize(self, obj):
        raise NotImplementedError()

    @abc.abstractmethod
    def deserialize(self, data):
        raise NotImplementedError()


class MsgPackSerializer(Serializer):
    cache = {}

    @staticmethod
    def decode(obj):
        if b'__datetime__' in obj:
            obj = datetime.datetime.strptime(obj["as_str"], "%Y%m%dT%H:%M:%S.%f")
        elif b'cls' in obj:
            data = obj
            module = obj[b'module']
            cls = obj[b'cls']
            if (module, cls) not in MsgPackSerializer.cache:
                m = importlib.import_module(module)
                c = getattr(m, cls)
                MsgPackSerializer.cache[(module, cls)] = c
            c = MsgPackSerializer.cache[(module, cls)]
            obj = c()
            obj.deserialize(data)
        return obj

    @staticmethod
    def encode(obj):
        if isinstance(obj, Serializable):
            return obj.serialize()
        if isinstance(obj, datetime.datetime):
            return {'__datetime__': True, 'as_str': obj.strftime("%Y%m%dT%H:%M:%S.%f")}

        return obj

    def serialize(self, obj):
        return msgpack.packb(obj, default=MsgPackSerializer.encode)

    def deserialize(self, data):
        return msgpack.unpackb(data, object_hook=MsgPackSerializer.decode)
