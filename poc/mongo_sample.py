from pymongo import MongoClient

from algotrader.event.market_data import Bar, Quote, Trade
from algotrader.utils.ser_deser import JsonSerializer
import random
import time
client = MongoClient('localhost', 27017)

db = client.market_data
bars = db.bars
# collection = db.test_collection



for unpacked in bars.find():
    bar = Bar()
    bar.deserialize(unpacked)
    print bar

# serializer = JsonSerializer()
#
# for x in range(0, 10):
#     data = sorted([random.randint(0, 100) for i in range(0, 4)])
#     bar = Bar(inst_id=3, open=data[1], high=data[3], low=data[0], close=data[2], vol=random.randint(100, 1000))
#
#
#     #print bar
#     packed = bar.serialize()
#     #print packed
#
#     bar_id = bars.insert_one(packed).inserted_id
#
#     #print bar_id
#     #print bars.find_one()
#     #print bars.find_one({"inst_id": "3"})
#
#     result = bars.find_one({"_id": bar_id})
#
#     unpacked = Bar()
#     unpacked.deserialize(result)
#     print unpacked, (unpacked == bar)
#
#     time.sleep(1)
#
#
#
