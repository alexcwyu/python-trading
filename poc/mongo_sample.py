import random
import time

from pymongo import MongoClient

from algotrader.config.persistence import MongoDBConfig
from algotrader.event.market_data import Bar
from algotrader.event.order import NewOrderRequest, OrdAction, OrdType
from algotrader.provider.persistence.mongodb import MongoDBDataStore
from algotrader.strategy.strategy_mgr import StrategyManager
from algotrader.trading.order_mgr import OrderManager
from algotrader.trading.portfolio_mgr import PortfolioManager
from algotrader.utils.ser_deser import JsonSerializer


def test1():
    client = MongoClient('localhost', 27017)

    db = client.market_data
    bars = db.bars
    # collection = db.test_collection



    # for unpacked in bars.find():
    #     bar = Bar()
    #     bar.deserialize(unpacked)
    #     print bar

    serializer = JsonSerializer()

    for x in range(0, 10):
        data = sorted([random.randint(0, 100) for i in range(0, 4)])
        bar = Bar(inst_id=3, open=data[1], high=data[3], low=data[0], close=data[2], vol=random.randint(100, 1000))

        # print bar
        packed = bar.serialize()
        id = bar.id()
        # if id:
        #    packed['_id'] = id

        print packed
        bars.update({'_id': id}, packed, upsert=True)

        # print bar_id
        # print bars.find_one()
        # print bars.find_one({"inst_id": "3"})

        result = bars.find_one({"_id": id})

        unpacked = Bar()
        unpacked.deserialize(result)
        print unpacked, (unpacked == bar)

        time.sleep(1)


def test_bar():
    config = MongoDBConfig()
    store = MongoDBDataStore(config)

    store.start()
    for x in range(0, 10):
        data = sorted([random.randint(0, 100) for i in range(0, 4)])
        bar = Bar(inst_id=3, open=data[1], high=data[3], low=data[0], close=data[2], vol=random.randint(100, 1000))

        store.save(bar)
        print bar
        time.sleep(1)


def test_save_portfolio():
    config = MongoDBConfig()
    store = MongoDBDataStore(config)

    portf_mgr = PortfolioManager()


def test_save_orders():
    config = MongoDBConfig()
    store = MongoDBDataStore(config)

    ord_mrg = OrderManager(store)

    store.start()
    order = ord_mrg.send_order(
        NewOrderRequest(cl_id='test', cl_ord_id=1, inst_id=1, action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000,
                        limit_price=18.5))
    order = ord_mrg.send_order(
        NewOrderRequest(cl_id='test', cl_ord_id=2, inst_id=1, action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000,
                        limit_price=18.5))

    before = ord_mrg.all_orders()

    ord_mrg.save()
    ord_mrg.load()

    after = ord_mrg.all_orders()

    print before
    print after


def test_save_strategies():
    config = MongoDBConfig()
    store = MongoDBDataStore(config)

    stg_mgr = StrategyManager()


def test_save_accounts():
    config = MongoDBConfig()
    store = MongoDBDataStore(config)


test_save_orders()
