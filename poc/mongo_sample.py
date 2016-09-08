import random
import time

from pymongo import MongoClient

from algotrader.config.app import ApplicationConfig
from algotrader.config.persistence import MongoDBConfig
from algotrader.event.market_data import Bar
from algotrader.event.order import NewOrderRequest, OrdAction, OrdType
from algotrader.provider.persistence import DataStore
from algotrader.provider.persistence.mongodb import MongoDBDataStore
from algotrader.strategy.strategy import Strategy
from algotrader.strategy.strategy_mgr import StrategyManager
from algotrader.trading.account import Account
from algotrader.trading.account_mgr import AccountManager
from algotrader.trading.context import ApplicationContext
from algotrader.trading.order import Order
from algotrader.trading.order_mgr import OrderManager
from algotrader.trading.portfolio import Portfolio
from algotrader.trading.portfolio_mgr import PortfolioManager
from algotrader.trading.seq_mgr import SequenceManager
from algotrader.utils.ser_deser import JsonSerializer


def get_default_app_context():
    config = MongoDBConfig()
    app_config = ApplicationConfig(None, DataStore.Mongo, DataStore.Mongo, DataStore.Mongo, DataStore.Mongo, None, None,
                                   config)
    return ApplicationContext(app_config=app_config)



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
    context = get_default_app_context()
    store = context.provider_mgr.get(DataStore.Mongo)
    store.start()

    portf_mgr = context.provider_mgr
    portf_mgr.start()

    p1 = Portfolio(portf_id=1, cash=1000)


    from algotrader.utils.ser_deser import MapSerializer

    v = MapSerializer.serialize(p1)
    print v
    #p2 = Portfolio(portf_id=2, cash=1000)

    portf_mgr.add(p1)
    #portf_mgr.add(p2)

    before = portf_mgr.get(1)

    portf_mgr.stop()
    portf_mgr.start()

    after = portf_mgr.get(1)
    print before
    print after


def test_save_orders():

    context = get_default_app_context()
    store = context.provider_mgr.get(DataStore.Mongo)
    store.start()

    ord_mrg = context.order_mgr

    ord_mrg.start()
    ord_mrg.reset()

    order = ord_mrg.send_order(
        NewOrderRequest(cl_id='test_stg', cl_ord_id=1, inst_id=1, portf_id='test_porf', action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000,
                        limit_price=18.5))
    order = ord_mrg.send_order(
        NewOrderRequest(cl_id='test_stg', cl_ord_id=2, inst_id=1, portf_id='test_porf', action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000,
                        limit_price=18.5))

    before = ord_mrg.all_items()

    ord_mrg.stop()
    ord_mrg.start()

    after = ord_mrg.all_items()

    print before
    print after


    p1 = Portfolio(portf_id='test_porf', cash=1000, app_context=context)
    p1.start()

    print "all"
    print p1.all_orders()



def test_save_strategies():
    config = MongoDBConfig()
    store = MongoDBDataStore(config)

    stg_mgr = StrategyManager(store)

    store.start()
    stg1 = Strategy(stg_id='st1', next_ord_id=0, trading_config=None, ref_data_mgr=None)
    nos = NewOrderRequest(cl_id='test', cl_ord_id='1', inst_id='1', action=OrdAction.BUY, type=OrdType.LIMIT, qty=1000,
                          limit_price=18.5)

    order = Order(nos=nos)
    stg1.ord_reqs[nos.cl_ord_id] = nos
    stg1.orders[order.cl_ord_id] = order
    stg1.add_position(nos.inst_id, nos.cl_id, nos.cl_ord_id, nos.qty)
    stg1.update_position_price(time=0, inst_id=nos.inst_id, price=100)

    stg2 = Strategy(stg_id='st2', next_ord_id=0, trading_config=None, ref_data_mgr=None)
    stg_mgr.add(stg1)
    stg_mgr.add(stg2)

    before = stg_mgr.all_items()

    stg_mgr.save()
    stg_mgr.load()

    after = stg_mgr.all_items()

    print before
    print after


def test_save_accounts():
    config = MongoDBConfig()
    store = MongoDBDataStore(config)

    acct_mgr = AccountManager(store)

    store.start()
    acct1 = Account(name="1")
    acct2 = Account(name="2")

    acct_mgr.add_account(acct1)
    acct_mgr.add_account(acct2)

    before = acct_mgr.all_accounts()

    acct_mgr.save()
    acct_mgr.load()

    after = acct_mgr.all_accounts()

    print before
    print after


def test_save_sequences():
    context = get_default_app_context()
    store = context.provider_mgr.get(DataStore.Mongo)
    store.start()

    seq_mgr = SequenceManager(context)
    seq_mgr.start()

    print seq_mgr.get_next_sequence("order")
    print seq_mgr.get_next_sequence("order")

    print seq_mgr.get_next_sequence("trade")
    print seq_mgr.get_next_sequence("trade")

    seq_mgr.stop()


#test_save_orders()


test_save_portfolio()