import numpy as np

from algotrader.technical import Indicator


def gain_loss(prev_value, next_value):
    change = next_value - prev_value
    if change < 0:
        gain = 0
        loss = abs(change)
    else:
        gain = change
        loss = 0
    print "change=%s, gain=%s, loss=%s"%(change, gain, loss)
    return gain, loss


# [begin, end)
def avg_gain_loss(series, begin, end):
    range_len = end - begin
    if range_len < 2:
        return 0, 0

    gain = 0
    loss = 0
    for i in xrange(begin + 1, end):
        curr_gain, curr_loss = gain_loss(series[i - 1], series[i])
        gain += curr_gain
        loss += curr_loss
    return gain / float(range_len - 1), loss / float(range_len - 1)


def rsi(values, length):
    assert (length > 1)
    if len(values) > length:

        avg_gain, avg_loss = avg_gain_loss(values, 0, length)
        for i in xrange(length, len(values)):
            gain, loss = gain_loss(values[i - 1], values[i])
            avg_gain = (avg_gain * (length - 1) + gain) / float(length)
            avg_loss = (avg_loss * (length - 1) + loss) / float(length)

        if avg_loss == 0:
            return 100
        rs = avg_gain / avg_loss
        return 100 - 100 / (1 + rs)
    else:
        return np.nan


class RSI(Indicator):
    _slots__ = (
        'length',
        '__prev_gain',
        '__prev_loss'
    )

    def __init__(self, input, length=14, description="Relative Strength Indicator"):
        super(RSI, self).__init__(input, "RSI(%s, %s)" % (input.id, length), description)
        self.length = length
        self.__prev_gain = None
        self.__prev_loss = None

    def on_update(self, time_value):
        time, value = time_value
        if self.input.size() > self.length:
            if self.__prev_gain is None:
                avg_gain, avg_loss = avg_gain_loss(self.input, 0, self.input.size())
                print "1. gain=%0.2f, loss=%0.2f"%(avg_gain, avg_loss)
            else:
                prev_value = self.input.ago(1)
                curr_value = self.input.now()
                curr_gain, curr_loss = gain_loss(prev_value, curr_value)
                avg_gain = (self.__prev_gain * (self.length - 1) + curr_gain) / float(self.length)
                avg_loss = (self.__prev_loss * (self.length - 1) + curr_loss) / float(self.length)

                print "2. gain=%0.2f, loss=%0.2f"%(avg_gain, avg_loss)

            if avg_loss == 0:
                rsi_value = 100
            else:
                rs = avg_gain / avg_loss
                rsi_value = 100 - 100 / (1 + rs)
                self.__prev_gain = avg_gain
                self.__prev_loss = avg_loss
                print "%0.2f, %0.2f"%(rs, rsi_value)

            self.add(time, rsi_value)
        else:
            self.add(time, np.nan)


if __name__ == "__main__":
    import datetime
    from algotrader.utils.time_series import TimeSeries
    close = TimeSeries("close")
    rsi = RSI(close, 14)

    t = datetime.datetime.now()


    values = [44.34, 44.09, 44.15, 43.61, 44.33, 44.83, 45.10, 45.42,
             45.84, 46.08, 45.89, 46.03, 45.61, 46.28, 46.28, 46.00]

    for idx, value in enumerate(values):
        close.add(t, value)
        t = t + datetime.timedelta(0, 3)

        print idx, rsi.now()