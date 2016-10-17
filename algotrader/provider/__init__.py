import abc

from algotrader import Startable, HasId


class Provider(Startable, HasId):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        super(Provider, self).__init__()
