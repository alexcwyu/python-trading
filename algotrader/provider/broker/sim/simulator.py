from collections import defaultdict

from algotrader.config.broker import SimulatorConfig
from algotrader.event.event_bus import EventBus
from algotrader.event.event_handler import MarketDataEventHandler
from algotrader.event.order import OrdStatus, OrderStatusUpdate, \
    ExecutionReport
from algotrader.provider.broker import Broker
from algotrader.provider.broker.sim.commission import NoCommission
from algotrader.provider.broker.sim.fill_strategy import DefaultFillStrategy
from algotrader.utils import logger


class Simulator(Broker, MarketDataEventHandler):
    def __init__(self):
        super(Simulator, self).__init__()
        self.ord_req_map = defaultdict(lambda: defaultdict(dict))
        self.ord_req_fill_status = defaultdict(dict)
        self.clordid_ordid_map = defaultdict(dict)
        self.quote_map = {}

    def get_fill_strategy(self, fill_strategy_id=None):
        return DefaultFillStrategy(self.app_context)

    def get_commission(self, commission_id=None):
        return NoCommission()

    def _start(self, app_context, **kwargs):
        self.app_context = app_context
        self.sim_config = app_context.app_config.get_config(SimulatorConfig)
        self.clock = app_context.clock
        # self.next_ord_id = self.sim_config.next_ord_id
        # self.next_exec_id = self.sim_config.next_exec_id
        self.fill_strategy = self.get_fill_strategy(self.sim_config.fill_strategy_id)
        self.commission = self.get_commission(self.sim_config.commission_id)
        self.exec_handler = self.app_context.order_mgr
        self.subscription = EventBus.data_subject.subscribe(self.on_next)

    def _stop(self):
        if self.subscription:
            self.subscription.dispose()

    def id(self):
        return Broker.Simulator

    def next_ord_id(self):
        return str(self.app_context.seq_mgr.get_next_sequence("%s.order" % self.id()))

    def next_exec_id(self):
        return self.app_context.seq_mgr.get_next_sequence("%s.exec" % self.id())

    def next_ord_status_id(self):
        return self.app_context.seq_mgr.get_next_sequence("%s.ordstatus" % self.id())

    def on_bar(self, bar):
        self.__process_event(bar)

    def on_quote(self, quote):
        self.__process_event(quote)

    def on_trade(self, trade):
        self.__process_event(trade)

    def __process_event(self, event):
        # SerializerTest.ser_deser(name, serializer, basket)
        logger.debug("[%s] %s" % (self.__class__.__name__, event))
        if event.inst_id in self.ord_req_map:
            for cl_ord_map in self.ord_req_map[event.inst_id].values():
                for new_ord_req in cl_ord_map.values():
                    fill_info = self.fill_strategy.process_w_market_data(new_ord_req, event, False)
                    executed = self.execute(new_ord_req, fill_info)

    def on_new_ord_req(self, new_ord_req):
        logger.debug("[%s] %s" % (self.__class__.__name__, new_ord_req))

        self.clordid_ordid_map
        self.__add_order(new_ord_req)
        self.__send_exec_report(new_ord_req, 0, 0, OrdStatus.SUBMITTED)

        fill_info = self.fill_strategy.process_new_order(new_ord_req)
        executed = self.execute(new_ord_req, fill_info)

    def __add_order(self, new_ord_req):
        ord_reqs = self.ord_req_map[new_ord_req.inst_id]
        ord_reqs[new_ord_req.cl_id][new_ord_req.cl_ord_id] = new_ord_req
        self.clordid_ordid_map[new_ord_req.cl_id][new_ord_req.cl_ord_id] = self.next_ord_id()

    def __remove_order(self, new_ord_req):
        if new_ord_req.inst_id in self.ord_req_map:
            ord_reqs = self.ord_req_map[new_ord_req.inst_id]
            if new_ord_req.cl_id in ord_reqs:
                if new_ord_req.cl_ord_id in ord_reqs[new_ord_req.cl_id]:
                    del ord_reqs[new_ord_req.cl_id][new_ord_req.cl_ord_id]

    def execute(self, new_ord_req, fill_info):
        if not fill_info or fill_info.fill_price <= 0 or fill_info.fill_price <= 0:
            return False

        # new_ord_req is removed
        if new_ord_req.inst_id not in self.ord_req_map:
            return False

        total_filled_qty = self.ord_req_fill_status[new_ord_req.cl_id].get(new_ord_req.cl_ord_id, 0)
        price = fill_info.fill_price
        qty = fill_info.fill_qty
        leave_qty = new_ord_req.qty - total_filled_qty

        if qty < leave_qty:
            total_filled_qty += qty
            self.ord_req_fill_status[new_ord_req.cl_id][new_ord_req.cl_ord_id] = total_filled_qty

            self.__send_exec_report(new_ord_req, price, qty, OrdStatus.PARTIALLY_FILLED)
            return False
        else:
            qty = leave_qty
            total_filled_qty += qty
            self.ord_req_fill_status[new_ord_req.cl_id][new_ord_req.cl_ord_id] = total_filled_qty

            self.__send_exec_report(new_ord_req, price, qty, OrdStatus.FILLED)
            self.__remove_order(new_ord_req)
            return True

    def __send_status(self, new_ord_req, ord_status):
        ord_id = self.clordid_ordid_map[new_ord_req.cl_id][new_ord_req.cl_ord_id]
        ord_update = OrderStatusUpdate(ord_status_id=self.next_ord_status_id(),
                                       broker_id=Broker.Simulator,
                                       ord_id=ord_id,
                                       cl_id=new_ord_req.cl_id,
                                       cl_ord_id=new_ord_req.cl_ord_id,
                                       inst_id=new_ord_req.inst_id,
                                       timestamp=self.clock.now(),
                                       status=ord_status)
        self.exec_handler.on_ord_upd(ord_update)

    def __send_exec_report(self, new_ord_req, last_price, last_qty, ord_status):
        commission = self.commission.calc(new_ord_req, last_price, last_qty)
        ord_id = self.clordid_ordid_map[new_ord_req.cl_id][new_ord_req.cl_ord_id]
        exec_report = ExecutionReport(broker_id=Broker.Simulator,
                                      ord_id=ord_id,
                                      cl_id=new_ord_req.cl_id,
                                      cl_ord_id=new_ord_req.cl_ord_id,
                                      inst_id=new_ord_req.inst_id,
                                      timestamp=self.clock.now(),
                                      er_id=self.next_exec_id(),
                                      last_qty=last_qty,
                                      last_price=last_price,
                                      status=ord_status,
                                      commission=commission)

        self.exec_handler.on_exec_report(exec_report)

    def _get_orders(self):
        return self.ord_req_map
