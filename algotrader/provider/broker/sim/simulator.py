from collections import defaultdict

from algotrader.event.event_bus import EventBus
from algotrader.event.market_data import MarketDataEventHandler
from algotrader.event.order import OrdStatus, OrderStatusUpdate, \
    ExecutionReport
from algotrader.provider.broker.sim.commission import NoCommission
from algotrader.provider.broker.sim.fill_strategy import DefaultFillStrategy
from algotrader.provider.provider import broker_mgr, Broker
from algotrader.trading import order_mgr
from algotrader.utils import clock
from algotrader.utils import logger


class Simulator(Broker, MarketDataEventHandler):
    ID = "Simulator"

    def __init__(self, exec_handler=order_mgr, commission=None, fill_strategy=None):

        super(Simulator, self).__init__()
        self.__next_exec_id = 0
        self.__order_map = defaultdict(dict)
        self.__quote_map = {}
        self.__exec__handler = exec_handler
        self.__fill_strategy = fill_strategy if fill_strategy is not None else DefaultFillStrategy()
        self.__commission = commission if commission is not None else NoCommission()

        broker_mgr.register(self)

    def start(self):
        EventBus.data_subject.subscribe(self.on_next)

    def stop(self):
        pass

    def id(self):
        return Simulator.ID

    def next_exec_id(self):
        __next_exec_id = self.__next_exec_id
        self.__next_exec_id += 1
        return __next_exec_id

    def on_bar(self, bar):
        self.__process_event(bar)

    def on_quote(self, quote):
        self.__process_event(quote)

    def on_trade(self, trade):
        self.__process_event(trade)

    def __process_event(self, event):
        logger.debug("[%s] %s" % (self.__class__.__name__, event))
        if event.inst_id in self.__order_map:
            for order in self.__order_map[event.inst_id].values():
                fill_info = self.__fill_strategy.process_w_market_data(order, event, False)
                executed = self.execute(order, fill_info)

    def on_order(self, order):
        logger.debug("[%s] %s" % (self.__class__.__name__, order))

        self.__add_order(order)
        self.__send_exec_report(order, 0, 0, OrdStatus.SUBMITTED)

        fill_info = self.__fill_strategy.process_new_order(order)
        executed = self.execute(order, fill_info)

    def __add_order(self, order):
        orders = self.__order_map[order.inst_id]
        orders[order.ord_id] = order

    def __remove_order(self, order):
        if order.inst_id in self.__order_map:
            orders = self.__order_map[order.inst_id]
            if order.ord_id in orders:
                del orders[order.ord_id]

    def execute(self, order, fill_info):
        if not fill_info or fill_info.fill_price <= 0 or fill_info.fill_price <= 0:
            return False

        price = fill_info.fill_price
        qty = fill_info.fill_qty

        if order.is_done():
            self.__remove_order(order)
            return False

        if qty < order.leave_qty():
            self.__send_exec_report(order, price, qty, OrdStatus.PARTIALLY_FILLED)
            return False
        else:
            qty = order.leave_qty()
            self.__send_exec_report(order, price, qty, OrdStatus.FILLED)
            self.__remove_order(order)
            return True

    def __send_status(self, order, ord_status):
        ord_update = OrderStatusUpdate(broker_id=Simulator.ID, ord_id=order.ord_id, inst_id=order.inst_id,
                                       timestamp=clock.default_clock.current_date_time(), status=ord_status)
        self.__exec__handler.on_ord_upd(ord_update)

    def __send_exec_report(self, order, last_price, last_qty, ord_status):
        commission = self.__commission.calc(order, last_price, last_qty)
        exec_report = ExecutionReport(broker_id=Simulator.ID, ord_id=order.ord_id, inst_id=order.inst_id,
                                      timestamp=clock.default_clock.current_date_time(), er_id=self.next_exec_id(),
                                      last_qty=last_qty,
                                      last_price=last_price, status=ord_status,
                                      commission=commission)

        self.__exec__handler.on_exec_report(exec_report)

    def _get_orders(self):
        return self.__order_map


simulator = Simulator();
