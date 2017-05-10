import numpy as np
from unittest import TestCase

from algotrader.technical import Indicator
from algotrader.technical.pipeline import PipeLine
from algotrader.technical.pipeline.cross_sessional_apply import Average, Abs, Tail, Sign, DecayLinear, Scale
from algotrader.technical.pipeline.cross_sessional_apply import Sum as GSSum
from algotrader.technical.pipeline.make_vector import MakeVector
from algotrader.technical.pipeline.pairwise import Minus
from algotrader.technical.pipeline.rank import Rank
from algotrader.technical.talib_wrapper import SMA
from algotrader.trading.context import ApplicationContext


class PipelineTest(TestCase):
    def setUp(self):
        self.app_context = ApplicationContext()

    def test_name(self):

        bar = self.app_context.inst_data_mgr.get_series("bar")
        bar.start(self.app_context)
        sma3 = SMA(inputs=bar, input_keys='close', length=3)
        sma20 = SMA(inputs=bar, input_keys='close', length=20)
        sma50 = SMA(inputs=bar, input_keys='close', length=50)
        sma3.start(self.app_context)
        sma20.start(self.app_context)
        sma50.start(self.app_context)

        rank = Rank(inputs=[sma3, sma20, sma50], input_keys='close')
        rank.start(self.app_context)
        self.assertEquals("Rank(SMA(bar[close],length=3)[close],SMA(bar[close],length=20)[close],SMA(bar[close],length=50)[close],ascending=True)",
                          rank.name)

        bar0 = self.app_context.inst_data_mgr.get_series("bar0")
        bar1 = self.app_context.inst_data_mgr.get_series("bar1")
        bar2 = self.app_context.inst_data_mgr.get_series("bar2")
        bar3 = self.app_context.inst_data_mgr.get_series("bar3")
        bar0.start(self.app_context)
        bar1.start(self.app_context)
        bar2.start(self.app_context)
        bar3.start(self.app_context)
        barlist = [bar0, bar1, bar2, bar3]

        avg = Average(inputs=barlist, input_keys='close')
        gssum = GSSum(inputs=barlist, input_keys='close')
        basket = MakeVector(inputs=barlist, input_keys='close')
        # TODO: the name printed by pipeline now break the "parse" machnism so we have to review it
        self.assertEquals("Average(bar0[close],bar1[close],bar2[close],bar3[close],length=1)", avg.name)
        self.assertEquals("Sum(bar0[close],bar1[close],bar2[close],bar3[close],length=1)", gssum.name)
        self.assertEquals("MakeVector(bar0[close],bar1[close],bar2[close],bar3[close],length=1)", basket.name)

        bar4 = self.app_context.inst_data_mgr.get_series("bar4")
        bar5 = self.app_context.inst_data_mgr.get_series("bar5")
        bar6 = self.app_context.inst_data_mgr.get_series("bar6")
        bar7 = self.app_context.inst_data_mgr.get_series("bar7")
        basket2 = MakeVector(inputs=[bar4, bar5, bar6, bar7], input_keys='close')
        self.assertEquals("MakeVector(bar4[close],bar5[close],bar6[close],bar7[close],length=1)", basket2.name)

        cross_basket_spread = Minus(inputs=[basket2, basket])
        self.assertEquals("Minus(MakeVector(bar4[close],bar5[close],bar6[close],bar7[close],length=1)[close],MakeVector(bar0[close],bar1[close],bar2[close],bar3[close],length=1)[close],length=1)", cross_basket_spread.name)

    def test_empty_at_initialize(self):
        close = self.app_context.inst_data_mgr.get_series("bar")
        close.start(self.app_context)
        sma3 = SMA(inputs=close, input_keys='close', length=3)
        sma20 = SMA(inputs=close, input_keys='close', length=20)
        sma50 = SMA(inputs=close, input_keys='close', length=50)

        sma3.start(self.app_context)
        sma20.start(self.app_context)

        rank = Rank(inputs=[sma3, sma20, sma50], input_keys='close')
        rank.start(self.app_context)
        self.assertEquals(0, len(rank.get_data()))

    def test_shape(self):
        close = self.app_context.inst_data_mgr.get_series("bar")
        close.start(self.app_context)

        sma3 = SMA(inputs=close, input_keys='close', length=3)
        sma20 = SMA(inputs=close, input_keys='close', length=20)
        sma50 = SMA(inputs=close, input_keys='close', length=50)

        sma3.start(self.app_context)
        sma20.start(self.app_context)
        sma50.start(self.app_context)

        rank = Rank(inputs=[sma3, sma20, sma50], input_keys='close')
        rank.start(self.app_context)
        try:
            np.testing.assert_almost_equal(np.array([1, 3]), rank.shape(), 5)
        except AssertionError as e:
            self.fail(e.message)

    def test_with_spread(self):
        bar0 = self.app_context.inst_data_mgr.get_series("bar0")
        bar1 = self.app_context.inst_data_mgr.get_series("bar1")
        bar2 = self.app_context.inst_data_mgr.get_series("bar2")
        bar3 = self.app_context.inst_data_mgr.get_series("bar3")

    def __np_assert_almost_equal(self, target, output, precision=10):
        try:
            np.testing.assert_almost_equal(target, output, precision)
        except AssertionError as e:
            self.fail(e.message)

    def test_sync(self):
        bar0 = self.app_context.inst_data_mgr.get_series("bar0")
        bar1 = self.app_context.inst_data_mgr.get_series("bar1")
        bar2 = self.app_context.inst_data_mgr.get_series("bar2")
        bar3 = self.app_context.inst_data_mgr.get_series("bar3")
        bar4 = self.app_context.inst_data_mgr.get_series("bar4")
        bar5 = self.app_context.inst_data_mgr.get_series("bar5")
        bar6 = self.app_context.inst_data_mgr.get_series("bar6")
        bar7 = self.app_context.inst_data_mgr.get_series("bar7")

        bar0.start(self.app_context)
        bar1.start(self.app_context)
        bar2.start(self.app_context)
        bar3.start(self.app_context)
        bar4.start(self.app_context)
        bar5.start(self.app_context)
        bar6.start(self.app_context)
        bar7.start(self.app_context)

        basket = MakeVector(inputs=[bar0, bar1, bar2, bar3], input_keys='close')
        basket2 = MakeVector(inputs=[bar4, bar5, bar6, bar7], input_keys='close')

        basket.start(self.app_context)
        basket2.start(self.app_context)

        basket_open = MakeVector(inputs=[bar0, bar1, bar2, bar3], input_keys='open')
        basket_open2 = MakeVector(inputs=[bar4, bar5, bar6, bar7], input_keys='open')
        cross_basket_spread = Minus(inputs=[basket2, basket], input_keys=PipeLine.VALUE)

        basket_open.start(self.app_context)
        basket_open2.start(self.app_context)
        cross_basket_spread.start(self.app_context)

        nan_arr = np.empty([1, 4])
        nan_arr[:] = np.nan

        t1 = 1
        bar0.add(data={"timestamp": t1, "close": 80.0, "open": 0})
        self.__np_assert_almost_equal(nan_arr, basket.now()["value"])

        bar1.add(data={"timestamp": t1, "close": 95.0, "open": 0})
        self.__np_assert_almost_equal(nan_arr, basket.now()["value"])

        bar2.add(data={"timestamp": t1, "close": 102.0, "open": 0})
        self.__np_assert_almost_equal(nan_arr, basket.now()["value"])

        sync_vec = np.array([[80.0, 95.0, 102.0, 105.0]])

        bar3.add(data={"timestamp": t1, "close": 105.0, "open": 0})
        self.__np_assert_almost_equal(sync_vec, basket.now()["value"])

        bar4.add(data={"timestamp": t1, "close": 102.0, "open": 0})
        bar5.add(data={"timestamp": t1, "close": 95.0, "open": 0})
        bar6.add(data={"timestamp": t1, "close": 107.0, "open": 0})
        bar7.add(data={"timestamp": t1, "close": 101.0, "open": 0})

        sync_vec2 = np.array([[102.0, 95.0, 107.0, 101.0]])
        self.__np_assert_almost_equal(sync_vec2, basket2.now()["value"])

        target_spread = np.array([[22.0, 0.0, 5.0, -4.0]])
        self.__np_assert_almost_equal(target_spread, cross_basket_spread.now()["value"])
        self.__np_assert_almost_equal(sync_vec, basket.now()["value"])

    # def test_nan_before_size(self):
    def test_with_multiple_bar(self):
        bar0 = self.app_context.inst_data_mgr.get_series("bar0")
        bar1 = self.app_context.inst_data_mgr.get_series("bar1")
        bar2 = self.app_context.inst_data_mgr.get_series("bar2")
        bar3 = self.app_context.inst_data_mgr.get_series("bar3")

        bar0.start(self.app_context)
        bar1.start(self.app_context)
        bar2.start(self.app_context)
        bar3.start(self.app_context)

        barlist = [bar0, bar1, bar2, bar3]

        rank = Rank(inputs=barlist, input_keys='close')
        avg = Average(inputs=barlist, input_keys='close')
        gssum = GSSum(inputs=barlist, input_keys='close')
        absv = Abs(inputs=barlist, input_keys='close')
        tail = Tail(inputs=barlist, input_keys='close', lb=94, ub=103, newval=101)
        signvec = Sign(inputs=barlist, input_keys='close')
        decaylinear = DecayLinear(inputs=barlist, input_keys='close', length=3)
        scale = Scale(inputs=barlist, input_keys='close')

        rank.start(self.app_context)
        avg.start(self.app_context)
        gssum.start(self.app_context)
        absv.start(self.app_context)
        tail.start(self.app_context)
        signvec.start(self.app_context)
        decaylinear.start(self.app_context)
        scale.start(self.app_context)

        t1 = 1
        bar_t1_array = np.array([80, 95, 102, 105])
        bar0.add(data={"timestamp": t1, "close": bar_t1_array[0], "open": 0})
        bar1.add(data={"timestamp": t1, "close": bar_t1_array[1], "open": 0})
        bar2.add(data={"timestamp": t1, "close": bar_t1_array[2], "open": 0})
        bar3.add(data={"timestamp": t1, "close": bar_t1_array[3], "open": 0})

        # self.assertEquals([{"timestamp": t1,
        #                     "name": "'Rank('bar0','bar1','bar2','bar3',close)'",
        #                     "value": np.arange(4)/3.0}],
        #                   rank.get_data())

        rank_target = np.arange(4) / 3.0
        rank_target = rank_target.reshape((1, 4))
        avg_target = np.array([[95.5]])
        sum_target = np.array([[382.0]])
        abs_target = np.array([[80.0, 95.0, 102.0, 105.0]])
        tail_target = np.array([[80.0, 101.0, 101.0, 105.0]])
        signvec_target = np.array([[1.0, 1.0, 1.0, 1.0]])
        scale_target = bar_t1_array / np.sum(bar_t1_array)
        scale_target = scale_target.reshape(1, 4)

        self.__np_assert_almost_equal(abs_target, absv.now()["value"])
        self.__np_assert_almost_equal(rank_target, rank.get_data()[0]["value"], 5)
        self.__np_assert_almost_equal(avg_target, avg.get_data()[0]["value"], 5)
        self.__np_assert_almost_equal(sum_target, gssum.get_data()[0]["value"], 5)
        self.__np_assert_almost_equal(tail_target, tail.get_data()[0]["value"], 5)
        self.__np_assert_almost_equal(signvec_target, signvec.get_data()[0]["value"], 5)
        self.__np_assert_almost_equal(scale_target, scale.get_data()[0]["value"], 5)

        t2 = t1 + 3
        bar_t2_array = np.array([85, 98, 101.5, 103])
        bar0.add(data={"timestamp": t2, "close": bar_t2_array[0], "open": 0})
        bar1.add(data={"timestamp": t2, "close": bar_t2_array[1], "open": 0})
        bar2.add(data={"timestamp": t2, "close": bar_t2_array[2], "open": 0})
        bar3.add(data={"timestamp": t2, "close": bar_t2_array[3], "open": 0})

        t3 = t2 + 3
        bar_t3_array = np.array([87, 91, 107.0, 115])
        bar0.add(data={"timestamp": t3, "close": bar_t3_array[0], "open": 0})
        bar1.add(data={"timestamp": t3, "close": bar_t3_array[1], "open": 0})
        bar2.add(data={"timestamp": t3, "close": bar_t3_array[2], "open": 0})
        bar3.add(data={"timestamp": t3, "close": bar_t3_array[3], "open": 0})

        stack = np.vstack([bar_t1_array, bar_t2_array, bar_t3_array])
        decaylinear_target = np.dot(np.arange(3, 0, -1), stack) / np.sum(np.arange(3, 0, -1))
        scale_target = bar_t3_array / np.sum(bar_t3_array)
        scale_target = scale_target.reshape(1, 4)
        self.__np_assert_almost_equal(decaylinear_target, decaylinear.now(keys=PipeLine.VALUE))
        self.__np_assert_almost_equal(scale_target, scale.now(keys=PipeLine.VALUE))

    def test_with_multi_bar_multi_indicator(self):
        bar0 = self.app_context.inst_data_mgr.get_series("bar0")
        bar1 = self.app_context.inst_data_mgr.get_series("bar1")

        bar0.start(self.app_context)
        bar1.start(self.app_context)

        sma_2_bar0 = SMA(inputs=bar0, input_keys="close", length=2)
        sma_4_bar0 = SMA(inputs=bar0, input_keys="close", length=4)
        sma_3_bar1 = SMA(inputs=bar1, input_keys="close", length=3)

        sma_2_bar0.start(self.app_context)
        sma_4_bar0.start(self.app_context)
        sma_3_bar1.start(self.app_context)

        rank = Rank(inputs=[sma_2_bar0, sma_3_bar1, sma_4_bar0], input_keys=Indicator.VALUE)
        rank.start(self.app_context)

        t = 1
        bar0.add(data={"timestamp": t, "close": 80.0, "open": 0})
        bar1.add(data={"timestamp": t, "close": 95.0, "open": 0})
        print(rank.now(keys=PipeLine.VALUE))

        t = t + 3
        bar0.add(data={"timestamp": t, "close": 85.0, "open": 0})
        bar1.add(data={"timestamp": t, "close": 93.0, "open": 0})
        print(rank.now(keys=PipeLine.VALUE))

        t = t + 3
        bar0.add(data={"timestamp": t, "close": 86.0, "open": 0})
        bar1.add(data={"timestamp": t, "close": 91.0, "open": 0})
        print(rank.now(keys=PipeLine.VALUE))

        t = t + 3
        bar0.add(data={"timestamp": t, "close": 90.0, "open": 0})
        bar1.add(data={"timestamp": t, "close": 95.0, "open": 0})
        print(rank.now(keys=PipeLine.VALUE))
