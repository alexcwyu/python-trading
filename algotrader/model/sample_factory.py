from algotrader.model.model_factory import *


class SampleFactory(object):
    def __init__(self):
        self.factory = ModelFactory()

    def sample_instrument(self):
        inst = self.factory.build_instrument('2800.HK', Instrument.STK, 'SEHK', 'HKD',
                                             '2800', ['NYSE', 'TSE'], "Finance", "Banking", 100, 0.05,
                                             self.factory.build_underlying(Underlying.FixedWeightBasket, [
                                                 self.factory.build_asset('0005.HK@SEHK', 0.1),
                                                 self.factory.build_asset('0001.HK@SEHK', 0.9)
                                             ]), self.factory.build_derivative_traits(DrivativeTraits.Call,
                                                                                      DrivativeTraits.European, 100.2,
                                                                                      20160101, 1),
                                             alt_symbols={'IB': '2800', 'RIC': '2800.HK'},
                                             alt_ids={'VALOREN': '123123', 'ISIN': '123123'})

        return inst

    def sample_underlying(self):
        underlying = self.factory.build_underlying(Underlying.FixedWeightBasket, [
            self.factory.build_asset('128.HK@SEHK', 0.1),
            self.factory.build_asset('0001.HK@SEHK', 0.9)
        ])
        return underlying

    def sample_derivative_traits(self):
        derivative_traits = self.factory.build_derivative_traits(DrivativeTraits.Call, DrivativeTraits.European, 100.2,
                                                                 20160101, 1)
        return derivative_traits

    def sample_asset(self):
        asset = self.factory.build_asset('128.HK@SEHK', 0.1)
        return asset

    def sample_exchange(self):
        exchange = self.factory.build_exchange('SEHK', 'The Stock Exchange of Hong Kong Limited', 'HK', 'HKEX',
                                               'HK_Holiday')
        return exchange

    def sample_currency(self):
        currency = self.factory.build_currency('HKD', 'Hong Kong Doller')
        return currency

    def sample_country(self):
        country = self.factory.build_country('US', 'United States of America', 'US_holiday')
        return country

    def sample_holiday(self):
        holiday = self.factory.build_holiday(20161102, 20161102, 0, 20161103, 0, HolidaySeries.Holiday.FullDay)
        return holiday

    def sample_trading_holidays(self):
        trading_holiday = self.factory.build_holiday_series("HK holiday",
                                                            [self.factory.build_holiday(20161102,
                                                                                        HolidaySeries.Holiday.FullDay,
                                                                                        20161102, 20161103),
                                                             self.factory.build_holiday(20161223,
                                                                                        HolidaySeries.Holiday.FullDay,
                                                                                        20161223, 20161226)])
        return trading_holiday

    def sample_trading_session(self):
        session = self.factory.build_trading_session(TradingHours.Session.Monday, 9000, TradingHours.Session.Monday,
                                                     1600, True)
        return session

    def sample_trading_hours(self):
        trading_hours = self.factory.build_trading_hours('SEHK_trdinghr', 'HK timezone',
                                                         self.factory.build_trading_session(TradingHours.Session.Sunday,
                                                                                            9000,
                                                                                            TradingHours.Session.Monday,
                                                                                            1600, True))
        return trading_hours

    def sample_timezone(self):
        timezone = self.factory.build_timezone("Venezuela Standard Time")
        return timezone

    def sample_data_series_item(self):
        ds_item = self.factory.build_data_series_item(0, {"high": 350.00, "low": 200.45, "close": 250.1})
        return ds_item

    def sample_data_series(self):
        ds = self.factory.build_data_series("HSI.BAR.86400", name="HSI.BAR.86400", desc="HSI", inputs=["HSI.BAR.1"],
                                            keys=["high", "low", "close"], default_output_key="close",
                                            missing_value_replace=0, start_time=0, end_time=999,
                                            items=[self.factory.build_data_series_item(0,
                                                                                       {"high": 350.00, "low": 200.45,
                                                                                        "close": 250.1}),
                                                   self.factory.build_data_series_item(1,
                                                                                       {"high": 1350.00, "low": 1200.45,
                                                                                        "close": 1250.1})]
                                            )
        return ds

    def sample_bar(self):
        bar = self.factory.build_bar("HSI@SEHK", Bar.Time, 86400, provider_id='IB', timestamp=12312,
                                     utc_time=12312, begin_time=12300, open=123, high=300, low=30, close=156, vol=500,
                                     adj_close=324, open_interest=123)

        return bar

    def sample_quote(self):
        quote = self.factory.build_quote("HSI@SEHK", provider_id="IB", timestamp=12312,
                                         utc_time=12312, bid=50, bid_size=34, ask=102.2, ask_size=1)
        return quote

    def sample_trade(self):
        trade = self.factory.build_trade("HSI@SEHK", provider_id="IB", timestamp=12312,
                                         utc_time=12312, price=123, size=123)
        return trade

    def sample_market_depth(self):
        md = self.factory.build_market_depth("HSI@SEHK", provider_id="IB", timestamp=12312, md_provider="H", position=0,
                                             operation=MarketDepth.Insert, side=MarketDepth.bid,
                                             price=123, size=123, utc_time=12313)

        return md

    def sample_new_order_request(self):
        req = self.factory.build_new_order_request(0, "BuyLowSellHigh", "1", portf_id="TestPortf",
                                                   broker_id="Simulator", inst_id="HSI@SEHK",
                                                   action=Buy, type=Limit, qty=4954.1,
                                                   limit_price=123.2, stop_price=123.2, tif=DAY, oca_tag="23",
                                                   params={"testparam1": "1", "testparam2": "2"})
        return req

    def sample_order_replace_request(self):
        req = self.factory.build_order_replace_request(0, "BuyLowSellHigh", "1", type=Limit, qty=4954.1,
                                                       limit_price=123.2, stop_price=123.2, tif=DAY, oca_tag="23",
                                                       params={"testparam1": "1", "testparam2": "2"})
        return req

    def sample_order_cancel_request(self):
        req = self.factory.build_order_cancel_request(0, "BuyLowSellHigh", "1",
                                                      params={"testparam1": "1", "testparam2": "2"})

        return req

    def sample_order_status_update(self):
        event = self.factory.build_order_status_update(0, "IB", "event_123", broker_ord_id="broker_1234",
                                                       cl_id="BuyLowSellHigh", cl_ord_id="clOrdId_1",
                                                       inst_id="HSI@SEHK", filled_qty=1231.0, avg_price=123.1,
                                                       status=New)
        return event

    def sample_execution_report(self):
        event = self.factory.build_execution_report(1, "IB", "event_123", broker_ord_id="broker_1234", er_id="er+1231",
                                                    cl_id="BuyLowSellHigh", cl_ord_id="clOrdId_1", inst_id="HSI@SEHK",
                                                    last_qty=100.1, last_price=21.1,
                                                    commission=0.8, filled_qty=1231.0, avg_price=123.1,
                                                    status=New)

        return event

    def sample_account_value(self):
        value = self.factory.build_account_value("equity", {"HKD": 1231, "USD": 28.8})
        return value

    def sample_account_update(self):
        event = self.factory.build_account_update(0, "IB", event_id="e_123", account_name="account1", values={
            "equity": self.factory.build_account_value("equity", {"HKD": 1231, "USD": 28.8}),
            "pnl": self.factory.build_account_value("pnl", {"HKD": 1231, "USD": 28.8})
        })

        return event

    def sample_portfolio_update(self):
        event = self.factory.build_portfolio_update(0, "IB", event_id="e_456", portf_id="BLSH", inst_id="HSI@SEHK",
                                                    position=10, mkt_price=123.1, mkt_value=1231, avg_cost=12.8,
                                                    unrealized_pnl=1230, realized_pnl=0.8)

        return event

    def sample_client_order_id(self):
        return self.factory.build_client_order_id("BLSH", "O1")

    def sample_position(self):
        position = self.factory.build_position("HSI@SEHK", 1000, filled_qty=20, cl_orders=[
            self.factory.build_client_order_id("BLSH", "O1"),
            self.factory.build_client_order_id("BLSH", "O2")
        ])

        return position

    def sample_account(self):
        account = self.factory.build_account("test_acct", values={
            "equity": self.factory.build_account_value("equity", {"HKD": 1231, "USD": 28.8}),
            "pnl": self.factory.build_account_value("pnl", {"HKD": 1231, "USD": 28.8})},
                                             positions={"HSI@SEHK": self.sample_position()})
        return account

    def sample_portfolio(self):
        portfolio = self.factory.build_portfolio("test_portf", positions={"HSI@SEHK": self.sample_position()},
                                                 performance=self.sample_performance(),
                                                 pnl=self.sample_pnl(),
                                                 drawdown=self.sample_drawdown())

        return portfolio

    def sample_performance(self):
        performance = self.factory.build_performance(total_equity=100, cash=23, stock_value=68.8,
                                                     performance_series=self.sample_data_series())
        return performance

    def sample_pnl(self):
        pnl = self.factory.build_pnl(18.8, pnl_series=self.sample_data_series())
        return pnl

    def sample_drawdown(self):
        drawdown = self.factory.build_drawdown(last_drawdown=-12, last_drawdown_pct=-0.5, high_equity=1231,
                                               low_equity=29, current_run_up=10, current_drawdown=-123,
                                               drawdown_series=self.sample_data_series())
        return drawdown

    def sample_config(self):
        config = self.factory.build_config(config_id="testConfig", values={"k1": "v1", "k2": "v2"})
        return config

    def sample_strategy(self):
        strategy = self.factory.build_strategy("BLSH", config_id="Config1",
                                               positions={"HSI@SEHK": self.sample_position()})
        return strategy

    def sample_order(self):
        order = self.factory.build_order("BuyLowSellHigh", "1", portf_id="TestPortf",
                                         broker_id="Simulator", inst_id="HSI@SEHK", creation_timestamp=1,
                                         action=Buy, type=Limit, qty=4954.1,
                                         limit_price=123.2, stop_price=123.2, tif=DAY, oca_tag="23",
                                         params={"testparam1": "1", "testparam2": "2"}, broker_ord_id="B01",
                                         update_timestamp=12, status=New,
                                         filled_qty=12312, avg_price=12, last_qty=12, last_price=2.8,
                                         stop_limit_ready=True, trailing_stop_exec_price=12)
        return order
