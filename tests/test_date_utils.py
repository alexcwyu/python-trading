import random

from unittest import TestCase

from algotrader.utils.date import *
import datetime
from datetime import timezone
from tests import empty_config
import pytz
from pytz import timezone
import time
import pandas as pd


"""

https://stackoverflow.com/questions/6999726/how-can-i-convert-a-datetime-object-to-milliseconds-since-epoch-unix-time-in-p

Method 1 (python 2.7 or above )
import datetime

epoch = datetime.datetime.utcfromtimestamp(0)

def unix_time_millis(dt):
    return (dt - epoch).total_seconds() * 1000.0
    
note: dt must be in UTC
    
Method 2: ( Python 3.x above )

time.mktime(dt.timetuple())*1000

But this truncated to second!

Method 3: ( Pyhon 3.3 or above )

https://docs.python.org/3.3/library/datetime.html#datetime.datetime.timestamp
dt.timestamp()




"""


class DateUtilsTest(TestCase):


    def test_datetime_to_ts(self):
        hkzone = timezone('Hongkong')
        dt = datetime.datetime(2017, 9, 24, 0, 22, 0, tzinfo=hkzone)
        datetime_to_unixtimemillis(dt)

        # this match with the this site
        # https://currentmillis.com
        time.mktime(dt.timetuple())*1000




    def test_date_with_timetuple_method(self):
        """
        this is not a test of algotrader impl
        this is an illustration that the timetuple() method is independent to timezone for date class
        :return:
        """
        hkzone = timezone('Hongkong')
        testday_with_tz = datetime.datetime(2017, 9, 24, tzinfo=hkzone)
        testdate = datetime.date(2017, 9, 24)
        testday_without_tz = datetime.datetime(2017, 9, 24)
        a = time.mktime(testdate.timetuple())*1000
        b = time.mktime(testday_with_tz.timetuple())*1000
        c = time.mktime(testday_without_tz.timetuple())*1000

        self.assertEqual(a, b)
        self.assertEqual(c, b)


    def test_date_with_timestamp_method(self):
        hkzone = timezone('Hongkong')
        dt_with_tz = datetime.datetime(2017, 9, 24, tzinfo=hkzone)
        dt_without_tz = datetime.datetime(2017, 9, 24)
        uts_with = dt_with_tz.timestamp()
        uts_without = dt_without_tz.timestamp()

        self.assertNotEqual(uts_without, uts_with)

        pd_with = pd.Timestamp(dt_with_tz)
        pd_without = pd.Timestamp(dt_without_tz)


        # this will raise exception
        #self.assertNotEqual(pd_with, pd_without)

        pd_unix_with_tz = pd_with.value // 10 ** 9
        pd_unix_without_tz = pd_without.value // 10 ** 9

        self.assertEqual(uts_with, pd_unix_with_tz)

        # Why they are not equals ? !!!!
        #self.assertEqual(uts_without, pd_unix_without_tz)
        #print("unix ts %s != %s converted from panadas" % (uts_without, pd_unix_without_tz))


        # convert back to datetime
        pd_dt_with_tz = pd_with.to_pydatetime()
        pd_dt_without_tz = pd_without.to_pydatetime()

        self.assertNotEqual(pd_dt_with_tz, dt_with_tz)

        # can even compare and raise exception
        # self.assertNotEqual(pd_dt_without_tz, dt_without_tz)




    def test_date(self):
        hkzone = timezone('Hongkong')
        testday_with_tz = datetime.datetime(2017, 9, 24, tzinfo=hkzone)
        testdate = datetime.date(2017, 9, 24)
        testday_without_tz = datetime.datetime(2017, 9, 24)
        a = date_to_unixtimemillis(testdate)
        b = date_to_unixtimemillis(testday_with_tz)
        c = date_to_unixtimemillis(testday_without_tz)

        self.assertEqual(a, b)
        self.assertEqual(c, b)
        target = time.mktime(testdate.timetuple())*1000
        self.assertEqual(a, target)

        # now test the pandas's method
        pd_val = pd.Timestamp(testdate).value // 10 ** 6
        self.assertEqual(pd_val, target)



