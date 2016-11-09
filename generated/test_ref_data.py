# protoc -I=model --python_out=generated model/*.proto

from datetime import date
from unittest import TestCase

import generated.ref_data_pb2 as ref_data
from algotrader.utils.date_utils import DateUtils
from protobuf_to_dict import *

class RefDataTest(TestCase):
    def test_instrument(self):
        inst = ref_data.Instrument()

        inst.id = 10
        inst.symbol = '0005.HK'
        inst.name = 'HSBC'
        inst.long_name = 'The Hongkong and Shanghai Banking Corporation'
        inst.type = ref_data.Instrument.CBO
        inst.primary_exch_id = 1
        inst.exch_ids.append(2)
        inst.exch_ids.append(3)
        inst.alt_symbols[1] = "5.HK"
        inst.alt_symbols[2] = "5"
        inst.alt_symbols[3] = "0005"
        inst.sector = 'finance'
        inst.industry = 'bank'
        inst.exp_date = DateUtils.date_to_unixtimemillis(date(2099, 12, 31))
        inst.call_put = ref_data.Instrument.Call
        inst.factor = 1.0
        inst.strike = 0.0
        inst.margin = 0.0
        inst.tick_size = 0.01
        inst.trading_hours_id = 1
        inst.trading_holidays_id = 1

        print(inst)


        b = inst.SerializeToString()
        inst2 = ref_data.Instrument()
        inst2.ParseFromString(b)
        self.assertEqual(inst, inst2)


        dict = protobuf_to_dict(inst)
        inst3 = dict_to_protobuf(ref_data.Instrument, dict)
        self.assertEqual(inst, inst3)

    def test_currency(self):
        currency = ref_data.Currency(id=1, code="HKD", name="Hong Kong Dollar", alt_codes={1: "HK", 2: "HKDD"})

        print(currency)

        b = currency.SerializeToString()
        currency2 = ref_data.Currency()
        currency2.ParseFromString(b)

        self.assertEqual(currency, currency2)

    def test_exchange(self):
        exchange = ref_data.Exchange(id=1, code="SEHK", name="The Stock Exchange of Hong Kong Limited"
                                     , alt_codes={1: "HKEX", 2: "HKX"})

        print(exchange)

        b = exchange.SerializeToString()
        exchange2 = ref_data.Exchange()
        exchange2.ParseFromString(b)

        self.assertEqual(exchange, exchange2)

    def test_country(self):
        country = ref_data.Country(id=1, code="HK", name="Hong Kong")

        print(country)

        b = country.SerializeToString()
        country2 = ref_data.Country()
        country2.ParseFromString(b)

        self.assertEqual(country, country2)

    def test_trading_holidays(self):
        holidays = ref_data.TradingHolidays(
            id=6,
            name = "HK holiday",
            holidays=[
                ref_data.TradingHolidays.Holiday(trading_date=1992,
                                                 start_date=19991222, start_time=900,
                                                 end_date=19991222, end_time=1600,
                                                 type=ref_data.TradingHolidays.Holiday.LateOpen,
                                                 desc="regular"),
                ref_data.TradingHolidays.Holiday(trading_date=1992,
                                                 start_date=19991223, start_time=900,
                                                 end_date=19991223, end_time=1600,
                                                 type=ref_data.TradingHolidays.Holiday.LateOpen,
                                                 desc="regular")
            ]

        )

        print(holidays)

        b = holidays.SerializeToString()
        holidays2 = ref_data.TradingHolidays()
        holidays2.ParseFromString(b)

        self.assertEqual(holidays, holidays2)

    def test_trading_hours(self):

        hours = ref_data.TradingHours(
            id = 29,
            name = "HK Sessions",
            timezone = "ASIA/HONG_KONG",
            sessions = [
                ref_data.TradingHours.Session(
                    start_weekdate=ref_data.TradingHours.Session.Monday, start_time=900,
                    end_weekdate=ref_data.TradingHours.Session.Monday, end_time=915,
                    eod=False
                ),
                ref_data.TradingHours.Session(
                    start_weekdate=ref_data.TradingHours.Session.Monday, start_time=930,
                    end_weekdate=ref_data.TradingHours.Session.Monday, end_time=1630,
                    eod=True
                )
            ]

        )

        print(hours)

        b = hours.SerializeToString()
        hours2 = ref_data.TradingHours()
        hours2.ParseFromString(b)

        self.assertEqual(hours, hours2)
