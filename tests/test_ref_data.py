# protoc -I=model --python_out=generated model/*.proto

from datetime import date
from unittest import TestCase

from google.protobuf import json_format

import algotrader.model.ref_data_pb2 as ref_data
from algotrader.model.protobuf_to_dict import *
from algotrader.utils.date import date_to_unixtimemillis


class RefDataTest(TestCase):
    def test_instrument(self):
        inst = ref_data.Instrument()

        inst.inst_id = "10"
        inst.name = 'HSBC'
        inst.symbol = '0005.HK'
        inst.type = ref_data.Instrument.CBO
        inst.primary_exch_id = "SEHK"
        inst.exch_ids.append("NYSE")
        inst.alt_symbols["IB"] = "5.HK"
        inst.alt_symbols["BBG"] = "5"
        inst.sector = 'finance'
        inst.industry = 'bank'
        inst.exp_date = date_to_unixtimemillis(date(2099, 12, 31))
        inst.option_type = ref_data.Instrument.Call
        inst.multiplier = 1.0
        inst.strike = 0.0
        inst.margin = 0.0
        inst.tick_size = 0.01
        print("##########")
        print(inst)

        string = inst.SerializeToString()
        print("##########")
        print(string)
        inst2 = ref_data.Instrument()
        inst2.ParseFromString(string)
        self.assertEqual(inst, inst2)

        json_string = json_format.MessageToJson(inst)
        print("##########")
        print(json_string)

        d = protobuf_to_dict(inst)
        print("##########")
        print(d)
        inst3 = dict_to_protobuf(ref_data.Instrument, d)
        self.assertEqual(inst, inst3)

    def test_currency(self):
        currency = ref_data.Currency(ccy_id="HKD", name="Hong Kong Dollar")

        print(currency)

        b = currency.SerializeToString()
        currency2 = ref_data.Currency()
        currency2.ParseFromString(b)

        self.assertEqual(currency, currency2)

    def test_exchange(self):
        exchange = ref_data.Exchange(exch_id="SEHK", name="The Stock Exchange of Hong Kong Limited")

        print(exchange)

        b = exchange.SerializeToString()
        exchange2 = ref_data.Exchange()
        exchange2.ParseFromString(b)

        self.assertEqual(exchange, exchange2)

    def test_country(self):
        country = ref_data.Country(country_id="HK", name="Hong Kong")

        print(country)

        b = country.SerializeToString()
        country2 = ref_data.Country()
        country2.ParseFromString(b)

        self.assertEqual(country, country2)

    def test_trading_holidays(self):
        holidays = ref_data.HolidaySeries(
            holidays_id="6",
            holidays=[
                ref_data.HolidaySeries.Holiday(trading_date=1992,
                                               start_date=19991222, start_time=900,
                                               end_date=19991222, end_time=1600,
                                               type=ref_data.HolidaySeries.Holiday.LateOpen,
                                               desc="regular"),
                ref_data.HolidaySeries.Holiday(trading_date=1992,
                                               start_date=19991223, start_time=900,
                                               end_date=19991223, end_time=1600,
                                               type=ref_data.HolidaySeries.Holiday.LateOpen,
                                               desc="regular")
            ]

        )

        print(holidays)

        b = holidays.SerializeToString()
        holidays2 = ref_data.HolidaySeries()
        holidays2.ParseFromString(b)

        self.assertEqual(holidays, holidays2)

    def test_trading_hours(self):
        hours = ref_data.TradingHours(
            trading_hours_id="29",
            timezone_id="ASIA/HONG_KONG",
            sessions=[
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
