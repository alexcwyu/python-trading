from algotrader import Startable, Context


class Application(Startable):
    DataImport = "DataImport"
    LiveTrading = "LiveTrading"
    BackTesting = "BackTesting"

    def _start(self, app_context: Context) -> None:
        try:
            self.init()
            self.run()
        finally:
            self.stop()

    def init(self) -> None:
        pass

    def run(self) -> None:
        pass

    def _stop(self) -> None:
        self.app_context.stop()
