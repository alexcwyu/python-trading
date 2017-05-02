from algotrader import Startable


class Application(Startable):
    DataImport = "DataImport"
    LiveTrading = "LiveTrading"
    BackTesting = "BackTesting"

    def _start(self, app_context):
        try:
            self.init()
            self.run()
        finally:
            self.stop()

    def init(self):
        pass

    def run(self):
        pass

    def _stop(self):
        self.app_context.stop()
