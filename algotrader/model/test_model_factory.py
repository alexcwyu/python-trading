from unittest import TestCase

from algotrader.model import *


class ModelFactoryTest(TestCase):
    def setUp(self):
        self.factory = ModelFactory()

    def test_instrument(self):
        inst = self.factory.build_instrument('2800.HK', Instrument.STK, 'SEHK', 'HKD',
                                             '2800', ['NYSE', 'TSE'], "Finance", "Banking", 100, 0.05,
                                              self.factory.build_underlying(Underlying.FixedWeightBasket, [
                self.factory.build_asset('0005.HK@SEHK', 0.1),
                self.factory.build_asset('0001.HK@SEHK', 0.9)
            ]), self.factory.build_derivative_traits(DrivativeTraits.Call, DrivativeTraits.European, 100.2,
                                                     20160101, 1), alt_symbols={'IB': '2800', 'RIC': '2800.HK'},
                                             alt_ids={'VALOREN': '123123', 'ISIN': '123123'})

        self.__test_serializaion(Instrument, inst)

    def test_underlying(self):
        underlying = self.factory.build_underlying(Underlying.FixedWeightBasket, [
            self.factory.build_asset('128.HK@SEHK', 0.1),
            self.factory.build_asset('0001.HK@SEHK', 0.9)
        ])
        self.__test_serializaion(Underlying, underlying)

    def test_derivative_traits(self):
        derivative_traits = self.factory.build_derivative_traits(DrivativeTraits.Call, DrivativeTraits.European, 100.2,
                                                                 20160101, 1)
        self.__test_serializaion(DrivativeTraits, derivative_traits)

    def test_asset(self):
        asset = self.factory.build_asset('128.HK@SEHK', 0.1)
        self.__test_serializaion(Underlying.Asset, asset)

    def test_exchange(self):
        exchange = self.factory.build_exchange('SEHK', 'The Stock Exchange of Hong Kong Limited', 'HK', 'HKEX',
                                               'HK_Holiday')
        self.__test_serializaion(Exchange, exchange)

    def test_currency(self):
        currency = self.factory.build_currency('HKD', 'Hong Kong Doller')
        self.__test_serializaion(Currency, currency)

    def test_country(self):
        country = self.factory.build_country('US', 'United States of America', 'US_holiday')
        self.__test_serializaion(Country, country)

    def test_holiday(self):
        holiday = self.factory.build_holiday(20161102, 20161102, 0, 20161103, 0, HolidaySeries.Holiday.FullDay)
        self.__test_serializaion(HolidaySeries.Holiday, holiday)

    def test_trading_holidays(self):
        trading_holiday = self.factory.build_trading_holidays("HK holiday",
                                                              [self.factory.build_holiday(20161102,
                                                                                          HolidaySeries.Holiday.FullDay,
                                                                                          20161102, 20161103),
                                                               self.factory.build_holiday(20161223,
                                                                                          HolidaySeries.Holiday.FullDay,
                                                                                          20161223, 20161226)])
        self.__test_serializaion(HolidaySeries, trading_holiday)

    def test_trading_session(self):
        session = self.factory.build_trading_session(TradingHours.Session.Monday, 9000, TradingHours.Session.Monday,
                                                     1600, True)
        self.__test_serializaion(TradingHours.Session, session)

    def test_trading_hours(self):
        trading_hours = self.factory.build_trading_hours('SEHK_trdinghr', 'HK timezone',
                                                         self.factory.build_trading_session(TradingHours.Session.Monday,
                                                                                            9000,
                                                                                            TradingHours.Session.Monday,
                                                                                            1600, True))
        self.__test_serializaion(TradingHours, trading_hours)

    def test_timezone(self):
        timezone = self.factory.build_timezone("Venezuela Standard Time")
        self.__test_serializaion(TimeZone, timezone)

    def __test_serializaion(self, cls, obj):
        print(obj)

        obj2 = cls()
        obj2.ParseFromString(obj.SerializeToString())
        self.assertEqual(obj, obj2)

        obj3 = dict_to_protobuf(cls, protobuf_to_dict(obj))
        self.assertEqual(obj, obj3)
