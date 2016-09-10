import datetime

from algotrader import HasId
from algotrader.utils import msgpack_numpy as m

m.patch()
import importlib
import msgpack
import abc
import json
from itertools import chain
from algotrader.utils.date_utils import DateUtils


class Serializable(HasId):
    def __eq__(self, other):
        return (isinstance(other, self.__class__)
                and MapSerializer.extract_slot(self) == MapSerializer.extract_slot(
            other) and self.__dict__ == other.__dict__)

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
        if not hasattr(obj, '__module__'):
            return MapSerializer._deep_serialize(obj)

        map = {}
        map['@p'] = obj.__module__
        map['@t'] = obj.__class__.__name__

        attr_list, transient_list = MapSerializer.extract_slot_and_transient(obj)
        transient_set = set(transient_list)
        if include_slots:
            slot_values = {s: getattr(obj, s) for s in attr_list if s not in transient_set and hasattr(obj, s)}
            map['__slots__'] = MapSerializer._deep_serialize(slot_values, include_slots, include_dict)
        if include_dict:
            dict_values = {k: v for k, v in obj.__dict__.iteritems() if k not in transient_set}
            map['__dict__'] = MapSerializer._deep_serialize(obj.__dict__, include_slots, include_dict)
        return map

    @staticmethod
    def extract_slot_and_transient(obj):
        attr_list = []
        transient_list = []
        for cls in obj.__class__.__mro__:
            attrs = getattr(cls, '__slots__', [])
            transients = getattr(cls, '__transient__', [])

            if isinstance(attrs, (list, tuple)):
                for attr in attrs:
                    attr_list.append(attr)
            else:
                attr_list.append(attrs)

            if isinstance(transients, (list, tuple)):
                for transient in transients:
                    transient_list.append(transient)
            else:
                transient_list.append(transients)

        return attr_list, transient_list

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
            return {MapSerializer.deserialize(k): MapSerializer._deep_serialize(v) for k, v in item.iteritems()}
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
                return DateUtils.timestamp_to_datetime(data[b'__datetime__'])
            elif b'__date__' in data:
                return DateUtils.timestamp_to_date(data[b'__date__'])
            # elif '__datetime__' in data:
            #     return DateUtils.timestamp_to_datetime(data["__datetime__"])
            # elif '__date__' in data:
            #     return DateUtils.timestamp_to_date(data["__date__"])
            elif b'@t' in data:
                data = data
                module = data[b'@p']
                cls = data[b'@t']
                if (module, cls) not in Serializer.cls_cache:
                    m = importlib.import_module(module)
                    if not hasattr(m, cls):
                        print data
                    c = getattr(m, cls)
                    Serializer.cls_cache[(module, cls)] = c
                c = Serializer.cls_cache[(module, cls)]
                obj = c()
                MapSerializer._deserialize_obj(obj, data)
                return obj
            else:
                return {MapSerializer.deserialize(k): MapSerializer.deserialize(v) for k, v in data.iteritems()}
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
