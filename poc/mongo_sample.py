from pymongo import MongoClient

from algotrader.event.market_data import Bar
from algotrader.utils.ser_deser import JsonSerializer

client = MongoClient('localhost', 27017)

db = client.market_data
bars = db.bars
# collection = db.test_collection



bar = Bar(inst_id=3, open=18, high=19, low=17, close=17.5, vol=1000)
# quote = Quote(inst_id=3, bid=18, ask=19, bid_size=200, ask_size=500)
# trade = Trade(inst_id=3, price=20, size=200)


serializer = JsonSerializer()

print bar
packed = bar.serialize()
print packed

bar_id = bars.insert_one(packed).inserted_id

print bar_id
print bars.find_one()
print bars.find_one({"inst_id": "3"})

result = bars.find_one({"_id": bar_id})

unpacked = Bar()
unpacked.deserialize(result)
print unpacked
