from algotrader.model.market_data_pb2 import *
from algotrader.model.model_factory import ModelFactory
from algotrader.model.ref_data_pb2 import *
from algotrader.model.trade_data_pb2 import *


class SampleFactory(object):
    def __init__(self):
        pass

    def sample_instrument(self):
        inst = ModelFactory.build_instrument(symbol='2800.HK', type=Instrument.STK, primary_exch_id='SEHK',
                                             ccy_id='HKD',
                                             name='2800', exch_ids=['NYSE', 'TSE'], sector="Finance",
                                             industry="Banking",
                                             margin=100, tick_size=0.05,
                                             alt_symbols={'IB': '2800', 'RIC': '2800.HK'},
                                             alt_ids={'VALOREN': '123123', 'ISIN': '123123'},
                                             underlying_type=Underlying.FixedWeightBasket,
                                             underlying_ids=['0005.HK@SEHK', '0001.HK@SEHK'],
                                             underlying_weights=[0.1, 0.9],
                                             option_type=Instrument.Call,
                                             option_style=Instrument.European,
                                             strike=100.5,
                                             exp_date=20160101)
        return inst

    def sample_exchange(self):
        exchange = ModelFactory.build_exchange('SEHK', 'The Stock Exchange of Hong Kong Limited', 'HK', 'HKEX',
                                               'HK_Holiday')
        return exchange

    def sample_currency(self):
        currency = ModelFactory.build_currency('HKD', 'Hong Kong Doller')
        return currency

    def sample_country(self):
        country = ModelFactory.build_country('US', 'United States of America', 'US_holiday')
        return country

    def sample_trading_holidays(self):
        trading_holiday = ModelFactory.build_holiday_series("HK holiday")
        ModelFactory.add_holiday(trading_holiday, 20161102,
                                 HolidaySeries.Holiday.FullDay,
                                 20161102, 20161103)
        ModelFactory.add_holiday(trading_holiday, 20161223,
                                 HolidaySeries.Holiday.FullDay,
                                 20161223, 20161226)
        return trading_holiday

    def sample_trading_hours(self):
        trading_hours = ModelFactory.build_trading_hours(trading_hours_id='SEHK_trdinghr', timezone_id='HK timezone'
                                                         )
        ModelFactory.add_trading_session(trading_hours,
                                         TradingHours.Session.Sunday,
                                         9000,
                                         TradingHours.Session.Monday,
                                         1600, True)
        return trading_hours

    def sample_timezone(self):
        timezone = ModelFactory.build_timezone("Venezuela Standard Time")
        return timezone

    def sample_time_series(self):
        ds = ModelFactory.build_time_series("HSI.BAR.86400", name="HSI.BAR.86400", desc="HSI", inputs=["HSI.BAR.1"],
                                            keys=["high", "low", "close"], default_output_key="close",
                                            missing_value_replace=0, start_time=0, end_time=999,
                                            )
        ModelFactory.add_time_series_item(ds, timestamp=0,
                                          data={"high": 350.00, "low": 200.45,
                                                "close": 250.1})
        ModelFactory.add_time_series_item(ds, timestamp=1,
                                          data={"high": 1350.00, "low": 1200.45,
                                                "close": 1250.1})

        return ds

    def sample_bar(self):
        bar = ModelFactory.build_bar("HSI@SEHK", Bar.Time, 86400, provider_id='IB', timestamp=12312,
                                     utc_time=12312, begin_time=12300, open=123, high=300, low=30, close=156, vol=500,
                                     adj_close=324, open_interest=123)

        return bar

    def sample_quote(self):
        quote = ModelFactory.build_quote("HSI@SEHK", provider_id="IB", timestamp=12312,
                                         utc_time=12312, bid=50, bid_size=34, ask=102.2, ask_size=1)
        return quote

    def sample_trade(self):
        trade = ModelFactory.build_trade("HSI@SEHK", provider_id="IB", timestamp=12312,
                                         utc_time=12312, price=123, size=123)
        return trade

    def sample_market_depth(self):
        md = ModelFactory.build_market_depth("HSI@SEHK", provider_id="IB", timestamp=12312, md_provider="H", position=0,
                                             operation=MarketDepth.Insert, side=MarketDepth.Bid,
                                             price=123, size=123, utc_time=12313)

        return md

    def sample_new_order_request(self):
        req = ModelFactory.build_new_order_request(0, "BuyLowSellHigh", "1", portf_id="TestPortf",
                                                   broker_id="Simulator", inst_id="HSI@SEHK",
                                                   action=Buy, type=Limit, qty=4954.1,
                                                   limit_price=123.2, stop_price=123.2, tif=DAY, oca_tag="23",
                                                   params={"testparam1": "1", "testparam2": "2"})
        return req

    def sample_order_replace_request(self):
        req = ModelFactory.build_order_replace_request(0, "BuyLowSellHigh", "1", "2", type=Limit, qty=4954.1,
                                                       limit_price=123.2, stop_price=123.2, tif=DAY, oca_tag="23",
                                                       params={"testparam1": "1", "testparam2": "2"})
        return req

    def sample_order_cancel_request(self):
        req = ModelFactory.build_order_cancel_request(0, "BuyLowSellHigh", "1", "2",
                                                      params={"testparam1": "1", "testparam2": "2"})

        return req

    def sample_order_status_update(self):
        event = ModelFactory.build_order_status_update(0, "IB", "event_123", broker_ord_id="broker_1234",
                                                       cl_id="BuyLowSellHigh", cl_ord_id="clOrdId_1",
                                                       inst_id="HSI@SEHK", filled_qty=1231.0, avg_price=123.1,
                                                       status=New)
        return event

    def sample_execution_report(self):
        event = ModelFactory.build_execution_report(1, "IB", "event_123", broker_ord_id="broker_1234",
                                                    cl_id="BuyLowSellHigh", cl_ord_id="clOrdId_1", inst_id="HSI@SEHK",
                                                    last_qty=100.1, last_price=21.1,
                                                    commission=0.8, filled_qty=1231.0, avg_price=123.1,
                                                    status=New)

        return event

    def sample_account_update(self):
        event = ModelFactory.build_account_update(0, "IB", broker_event_id="e_123", account_name="account1")

        ModelFactory.update_account_value(event.values["equity"], key="equity", ccy_values={"HKD": 1231, "USD": 28.8})
        ModelFactory.update_account_value(event.values["pnl"], key="pnl", ccy_values={"HKD": 1231, "USD": 28.8})
        return event

    def sample_portfolio_update(self):
        event = ModelFactory.build_portfolio_update(0, "IB", broker_event_id="e_456", portf_id="BLSH",
                                                    inst_id="HSI@SEHK",
                                                    position=10, mkt_price=123.1, mkt_value=1231, avg_cost=12.8,
                                                    unrealized_pnl=1230, realized_pnl=0.8)

        return event

    def add_sample_position(self, attribute):
        position = ModelFactory.add_position(attribute=attribute, inst_id="HSI@SEHK", ordered_qty=1000, filled_qty=20,
                                             last_price=120.0)

        self.add_sample_order_position(position=position)
        return position

    def add_sample_order_position(self, position):
        ModelFactory.add_order_position(position, "BLSH", "O1", 100, 20)
        ModelFactory.add_order_position(position, "BLSH", "O2", 100, 50)

    def sample_account_state(self):
        account = ModelFactory.build_account_state("test_acct")
        ModelFactory.update_account_value(account.values["equity"], key="equity", ccy_values={"HKD": 1231, "USD": 28.8})
        ModelFactory.update_account_value(account.values["pnl"], key="pnl", ccy_values={"HKD": 1231, "USD": 28.8})
        self.add_sample_position(account)
        return account

    def sample_portfolio_state(self):
        portfolio = ModelFactory.build_portfolio_state("test_portf", cash=1000)
        self.add_sample_position(portfolio)
        return portfolio

    def sample_strategy_state(self):
        strategy = ModelFactory.build_strategy_state("BLSH")

        self.add_sample_position(strategy)
        return strategy

    def sample_order_state(self):
        order = ModelFactory.build_order_state("BuyLowSellHigh", "1", portf_id="TestPortf",
                                               broker_id="Simulator", inst_id="HSI@SEHK", creation_timestamp=1,
                                               action=Buy, type=Limit, qty=4954.1,
                                               limit_price=123.2, stop_price=123.2, tif=DAY, oca_tag="23",
                                               params={"testparam1": "1", "testparam2": "2"}, broker_ord_id="B01",
                                               update_timestamp=12, status=New,
                                               filled_qty=12312, avg_price=12, last_qty=12, last_price=2.8,
                                               stop_limit_ready=True, trailing_stop_exec_price=12)
        return order

    def sample_sequence(self):
        seq = ModelFactory.build_sequence("test_seq", 999)
        return seq
