from zerorpc.events import Event

import msgpack
from algotrader.utils.ser_deser import *


def pack(self):
    return msgpack.Packer(default=encode).pack((self._header, self._name, self._args))


@staticmethod
def unpack(blob):
    unpacker = msgpack.Unpacker(object_hook=decode)
    unpacker.feed(blob)
    unpacked_msg = unpacker.unpack()

    try:
        (header, name, args) = unpacked_msg
    except Exception as e:
        raise Exception('invalid msg format "{0}": {1}'.format(
            unpacked_msg, e))

    # Backward compatibility
    if not isinstance(header, dict):
        header = {}

    return Event(name, args, None, header)


Event.pack = pack
Event.unpack = unpack