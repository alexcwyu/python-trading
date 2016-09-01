import datetime

from rx.subjects import Subject

from algotrader.utils import msgpack_numpy as m

m.patch()
import importlib
import msgpack
import abc
import json
from itertools import chain
from algotrader.utils.date_utils import DateUtils



class Serializable(object):

    def __eq__(self, other):
        return (isinstance(other, self.__class__)
                and MapSerializer.extract_slot(self) == MapSerializer.extract_slot(other) and self.__dict__ == other.__dict__)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        items = ("%s = %r" % (k, v) for k, v in chain(MapSerializer.extract_slot(self).items(), self.__dict__.items()))
        return "%s(%s)" % (self.__class__.__name__, ', '.join(items))


class Serializer(object):
    primitive = (int, str, bool, float, long, complex, basestring)
    cls_cache = {}
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def serialize(self, obj):
        raise NotImplementedError()

    @abc.abstractmethod
    def deserialize(self, data):
        raise NotImplementedError()


class MapSerializer(Serializer):
    @staticmethod
    def serialize(obj, include_slots=True, include_dict=False):
        map = {}
        map['@p'] = obj.__module__
        map['@t'] = obj.__class__.__name__
        if include_slots:
            map['__slots__'] = MapSerializer._deep_serialize(MapSerializer.extract_slot(obj), include_slots, include_dict)
        if include_dict:
            map['__dict__'] = MapSerializer._deep_serialize(obj.__dict__, include_slots, include_dict)
        return map

    @staticmethod
    def extract_slot(obj):
        attr_list = []
        for cls in obj.__class__.__mro__:
            attrs = getattr(cls, '__slots__', [])
            if isinstance(attrs, (list, tuple)):
                attr_list.append(attrs)
            else:
                attr_list.append([attrs])
        return {s: getattr(obj, s) for s in chain.from_iterable(attr_list) if hasattr(obj, s)}

    @staticmethod
    def _deep_serialize(item, include_slots=True, include_dict=False):
        if isinstance(item, Serializable):
            return MapSerializer.serialize(item, include_slots, include_dict)
        elif isinstance(item, list):
            return [MapSerializer._deep_serialize(i) for i in item]
        elif isinstance(item, dict):
            return {k: MapSerializer._deep_serialize(v) for k, v in item.iteritems()}
        elif isinstance(item, tuple):
            return tuple([MapSerializer._deep_serialize(i) for i in item])
        elif isinstance(item, set):
            return set([MapSerializer._deep_serialize(i) for i in item])
        elif isinstance(item, datetime.datetime):
            return {'__datetime__': DateUtils.datetime_to_timestamp(item)}
        elif isinstance(item, datetime.date):
            return {'__date__': DateUtils.date_to_timestamp(item)}
        else:
            return item

    @staticmethod
    def deserialize(data):
        if isinstance(data, dict):
            if b'__datetime__' in data:
                return DateUtils.timestamp_to_datetime(data["__datetime__"])
            elif b'__date__' in data:
                return DateUtils.timestamp_to_date(data["__date__"])
            elif b'@t' in data:
                data = data
                module = data[b'@p']
                cls = data[b'@t']
                if (module, cls) not in Serializer.cls_cache:
                    m = importlib.import_module(module)
                    c = getattr(m, cls)
                    Serializer.cls_cache[(module, cls)] = c
                c = Serializer.cls_cache[(module, cls)]
                obj = c()
                MapSerializer._deserialize_obj(obj, data)
                return obj
        elif isinstance(data, list):
            return [MapSerializer.deserialize(i) for i in data]
        elif isinstance(data, tuple):
            return tuple([MapSerializer.deserialize(i) for i in data])
        elif isinstance(data, set):
            return set([MapSerializer.deserialize(i) for i in data])
        elif isinstance(data, basestring):
            return str(data)
        return data

    @staticmethod
    def _deserialize_obj(obj, map):

        if '__slots__' in map:
            data = map['__slots__']
            for k, v in data.items():
                setattr(obj, k, MapSerializer.deserialize(v))
        if '__dict__' in map:
            data = map['__dict__']
            for k, v in data.items():
                obj.__dict__[k] = MapSerializer.deserialize(v)


class MsgPackSerializer(Serializer):
    @staticmethod
    def serialize(obj):
        return msgpack.packb(obj, default=MapSerializer.serialize)
    @staticmethod
    def deserialize(data):
        return msgpack.unpackb(data, object_hook=MapSerializer.deserialize)


class JsonSerializer(Serializer):
    @staticmethod
    def serialize(obj):
        return json.dumps(obj, default=MapSerializer.serialize)

    @staticmethod
    def deserialize(data):
        return json.loads(data, object_hook=MapSerializer.deserialize)
