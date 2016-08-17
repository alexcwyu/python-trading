from algotrader.provider.persistence.persist import DataStore

from qpython import qconnection
from qpython.qtype import QException
from qpython.qconnection import MessageType
from qpython.qcollection import QTable


class KDBDataStore(DataStore):
    def __init__(self, config):
        self.config = config

    def start(self):
        self.q = qconnection.QConnection(host = 'localhost', port = 5000)
        self.started = True

    def stop(self):
        if self.started:
            self.q.close()