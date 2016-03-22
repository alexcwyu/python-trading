from collections import OrderedDict
import pandas as pd

d = OrderedDict()

d["test"] = 1
d["bar"] = 2
d["foo"] = 3
d["foo"] = 4
d["foo2"] = 5

print d

print len(d)

s = pd.Series(d, name='Value')
s.index.name = 'Time'

print s

print d.items()[-1][1]