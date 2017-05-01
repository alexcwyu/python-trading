import abc
from algotrader import HasId

from algotrader.utils.ser_deser import Serializable


class PersistenceMode(object):
    Disable = "Disable"
    Batch = "Batch"
    RealTime = "RealTime"


class Persistable(Serializable, HasId):
    __metaclass__ = abc.ABCMeta

    def save(self, data_store):
        pass

    def load(self):
        pass
