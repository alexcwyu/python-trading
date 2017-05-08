import numpy
from bidict import bidict
from typing import Dict, Callable, Union

from algotrader.model.market_data_pb2 import *
from algotrader.model.ref_data_pb2 import *
from algotrader.model.time_series_pb2 import *
from algotrader.model.trade_data_pb2 import *
from algotrader.utils.protobuf_to_dict import protobuf_to_dict, dict_to_protobuf

model_str_map = {
    Instrument: lambda inst: 'Inst {}'.format(inst.inst_id),
    Exchange: lambda exchange: 'Exchange {}'.format(exchange.exch_id),
    Currency: lambda currency: 'Currency {}'.format(currency.ccy_id),
    Country: lambda country: 'Country {}'.format(country.country_id),

    TimeSeries: lambda time_series: 'TimeSeries {}'.format(time_series.series_id),

    Bar: lambda bar: 'Bar {} provider_id={}, type={}, size={}, timestamp={}, open={}, high={}, low={} ,close={}'
        .format(bar.inst_id, bar.provider_id, bar.type, bar.size, bar.timestamp, bar.open, bar.high, bar.low,
                bar.close),

    Quote: lambda quote: 'Quote {} provider_id={}, timestamp={}, bid={}, ask={}'.format(quote.inst_id,
                                                                                        quote.provider_id,
                                                                                        quote.timestamp, quote.bid,
                                                                                        quote.ask),
    Trade: lambda trade: 'Trade {} provider_id={}, timestamp={}, last={}'.format(trade.inst_id, trade.provider_id,
                                                                                 trade.timestamp, trade.last),
    MarketDepth: lambda md: 'MarketDepth {} provider_id={}, timestamp={}'.format(md.inst_id, md.provider_id,
                                                                                 md.timestamp)
}

model_id_map = {
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

model_db_map = bidict({
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


def get_model_id(object):
    t = type(object)
    if t in model_id_map:
        return model_id_map[t](object)
    return object.id()


def get_model_db(object):
    t = type(object)
    return model_db_map[t]


def get_model_from_db_name(db):
    return model_db_map.inv[db]


def model_to_str(object) -> str:
    t = type(object)
    if t in model_str_map:
        return model_str_map[t](object)
    return object


def model_to_dict(obj):
    return protobuf_to_dict(obj)


def dict_to_model(cls, data):
    return dict_to_protobuf(cls, data)


def add_to_dict(attribute: Callable, dict: Dict[str, str]):
    if dict:
        for key, value in dict.items():
            if isinstance(value, (int, str, bool, float)):
                attribute[key] = value
            elif isinstance(value, (numpy.int64, numpy.int32, numpy.float32, numpy.float64)):
                attribute[key] = numpy.asscalar(value)
            else:
                raise RuntimeError


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
