import json
import sys

import simplejson
try:
    import ujson
except ImportError:
    pass
import tnetstring
import pickle
import cPickle
import functools


class P(object):
    pass

pickle2 = P()
pickle2.dumps = functools.partial(pickle.dumps, protocol=2)
pickle2.loads = pickle.loads
sys.modules['pickle2'] = pickle2

cPickle2 = P()
cPickle2.dumps = functools.partial(cPickle.dumps, protocol=2)
cPickle2.loads = cPickle.loads
sys.modules['cPickle2'] = cPickle2

try:
    import __pypy__
    tnetstrng = tnetstring
    tnetstring = P()
    tnetstring.dumps = functools.partial(tnetstrng.dumps, encoding="utf8")
    tnetstring.loads = functools.partial(tnetstrng.loads, encoding="utf8")
    sys.modules['tnetstring'] = tnetstring
except:
    pass

# test.json generated from http://www.json-generator.com/
# http://www.json-generator.com/api/json/get/cvfsLVmKiG?indent=2
testdict = simplejson.load(open('test.json','rb'))

def thrasher(serializer):
    m = sys.modules[serializer]
    dumper = getattr(m, 'dumps')
    loader = getattr(m, 'loads')
    def thrash():
        assert loader(dumper(testdict)) == testdict
    return thrash


def thrash_loads(serializer):
    m = sys.modules[serializer]
    dumper = getattr(m, 'dumps')
    loader = getattr(m, 'loads')
    data = dumper(testdict)
    def thrash():
        loader(data)
    return thrash

def thrash_dumps(serializer):
    m = sys.modules[serializer]
    dumper = getattr(m, 'dumps')
    def thrash():
        dumper(testdict)
    return thrash


PERMUTATIONS=10000

def print_round(name, tx, to, l=0, jl=0):
    if l or jl:
        print "%12s:\t%f\t%7.2f%%\t%d\t%7.2f%%" % (
            name, tx,
            round((tx / to) * 100,2),
            l,
            round((l / jl) * 100,2))
    else:
        print "%12s:\t%f\t%7.2f%%" % (
            name, tx,
            round((tx / to) * 100,2))


if __name__ == "__main__":
    import timeit
    tmodules = ("simplejson", "ujson", "tnetstring", "msgpack", "cbor",
                "marshal", "pickle", "pickle2", "cPickle", "cPickle2")
    if len(sys.argv) > 1:
        tmodules = sys.argv[1].split(',')

    print "..::DUMPS::.."
    print "%12s\t%s\t\t%s\t%s\t%s" % ("serializer","time","time-diff","size", "size-diff")
    to = timeit.Timer(
        "dumps()",
        "from tests.serialization_test import thrash_dumps;dumps=thrash_dumps('json')")
    to =to.timeit(number=PERMUTATIONS)
    jlen = float(len(json.dumps(testdict)))
    print_round("json", to, to, jlen, jlen)

    for x in tmodules:
        try:
            tx = timeit.Timer(
                "dumps()",
                "from tests.serialization_test import thrash_dumps;dumps=thrash_dumps('%s')" % x)
            tx = tx.timeit(number=PERMUTATIONS)
            m = sys.modules[x]
            print_round(x, tx, to, len(m.dumps(testdict)), jlen)
        except Exception as e:
            print "%12s: tests failed: %s" % (x, e)

    print ""

    print "..::LOADS::.."
    print "%12s\t%s\t\t%s" % ("serializer","time","time-diff")
    to = timeit.Timer(
        "loads()",
        "from tests.serialization_test import thrash_loads;loads=thrash_loads('json')")
    to =to.timeit(number=PERMUTATIONS)
    print_round("json", to, to)

    for x in tmodules:
        try:
            tx = timeit.Timer(
                "loads()",
                "from tests.serialization_test import thrash_loads;loads=thrash_loads('%s')" % x)
            tx = tx.timeit(number=PERMUTATIONS)
            m = sys.modules[x]
            print_round(x, tx, to)
        except Exception as e:
            print "%12s: tests failed: %s" % (x, e)