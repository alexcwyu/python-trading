from typing import Dict, Callable, Union

import numpy
from bidict import bidict

from algotrader.model.market_data_pb2 import *
from algotrader.model.protobuf_to_dict import *
from algotrader.model.ref_data_pb2 import *
from algotrader.model.time_series_pb2 import *
from algotrader.model.trade_data_pb2 import *


class ModelHelper(object):
    id_map = {
        Instrument: lambda inst: inst.inst_id,
        Exchange: lambda exchange: exchange.exch_id,
        Currency: lambda currency: currency.ccy_id,
        Country: lambda country: country.country_id,
        HolidaySeries: lambda holiday_series: holiday_series.holidays_id,
        TradingHours: lambda trading_hour: trading_hour.trading_hours_id,
        TimeZone: lambda timezone: timezone.timezone_id,

        TimeSeries: lambda time_series: time_series.series_id,

        Bar: lambda bar: 'Bar.{}.{}.{}.{}.{}'.format(bar.inst_id, bar.type, bar.size, bar.provider_id, bar.timestamp),
        Quote: lambda quote: 'Quote.{}.{}.{}'.format(quote.inst_id, quote.provider_id, quote.timestamp),
        Trade: lambda trade: 'Trade.{}.{}.{}'.format(trade.inst_id, trade.provider_id, trade.timestamp),
        MarketDepth: lambda md: 'MarketDepth.{}.{}.{}'.format(md.inst_id, md.provider_id, md.timestamp),

        NewOrderRequest: lambda req: '{}.{}'.format(req.cl_id, req.cl_ord_id),
        OrderReplaceRequest: lambda req: '{}.{}'.format(req.cl_id, req.cl_ord_id),
        OrderCancelRequest: lambda req: '{}.{}'.format(req.cl_id, req.cl_ord_id),

        OrderStatusUpdate: lambda event: '{}.{}'.format(event.broker_id, event.broker_event_id),
        ExecutionReport: lambda event: '{}.{}'.format(event.broker_id, event.broker_event_id),
        AccountUpdate: lambda event: '{}.{}'.format(event.broker_id, event.broker_event_id),
        PortfolioUpdate: lambda event: '{}.{}'.format(event.broker_id, event.broker_event_id),

        AccountState: lambda acct: acct.acct_id,
        PortfolioState: lambda portfolio: portfolio.portf_id,
        StrategyState: lambda strategy: strategy.stg_id,
        OrderState: lambda order: '{}.{}'.format(order.cl_id, order.cl_ord_id),
        # Config: lambda config: config.config_id,
        Sequence: lambda seq: seq.id,

    }

    db_map = bidict({
        Instrument: "instruments",
        Exchange: "exchanges",
        Currency: "currencies",
        # Country: "countries",
        # HolidaySeries: "holiday_series",
        # TradingHours: "trading_hours",
        # TimeZone: "time_zones",

        TimeSeries: "time_series",

        Bar: "bars",
        Quote: "quotes",
        Trade: "trades",
        MarketDepth: "market_depths",

        NewOrderRequest: "new_order_reqs",
        OrderReplaceRequest: "ord_replace_reqs",
        OrderCancelRequest: "ord_cancel_reqs",

        OrderStatusUpdate: "ord_status_upds",
        ExecutionReport: "exec_reports",
        AccountUpdate: "account_updates",
        PortfolioUpdate: "portfolio_updates",

        AccountState: "accounts",
        PortfolioState: "portfolios",
        StrategyState: "strategies",
        OrderState: "orders",
        # Config: "configs",
        Sequence: "sequences",

    })

    @staticmethod
    def get_id(object):
        t = type(object)
        return ModelHelper.id_map[t](object)

    @staticmethod
    def get_db(object):
        t = type(object)
        return ModelHelper.db_map[t]

    @staticmethod
    def get_type(db):
        return ModelHelper.db_map.inv[db]

    @staticmethod
    def object_to_dict(obj):
        return protobuf_to_dict(obj)

    @staticmethod
    def dict_to_object(cls, data):
        return dict_to_protobuf(cls, data)

    @staticmethod
    def add_to_dict(attribute: Callable, dict: Dict[str, str]):
        if dict:
            for key, value in dict.items():
                if isinstance(value, (int, str, bool, float)):
                    attribute[key] = value
                elif isinstance(value, (numpy.int64, numpy.int32, numpy.float32, numpy.float64)):
                    attribute[key] = numpy.asscalar(value)
                else:
                    raise RuntimeError

    @staticmethod
    def add_to_list(attribute: Callable, list_item: Union[list, tuple, int, str, bool, float, int]):
        if list_item:
            if not isinstance(list_item, (list, tuple)):
                list_item = list(list_item)

            for item in list_item:
                if isinstance(item, (int, str, bool, float)):
                    attribute.append(item)
                elif item is dict:
                    attribute.add(**item)
                else:
                    raise RuntimeError
