import random
import time

from pymongo import MongoClient

from algotrader.config.app import ApplicationConfig
from algotrader.config.persistence import MongoDBConfig, PersistenceConfig
from algotrader.config.app import BacktestingConfig
from algotrader.event.market_data import Bar
from algotrader.event.order import NewOrderRequest, OrdAction, OrdType
from algotrader.provider.persistence import PersistenceMode
from algotrader.provider.persistence.data_store import DataStore
from algotrader.provider.persistence.mongodb import MongoDBDataStore
from algotrader.trading.account_mgr import AccountManager
from algotrader.trading.context import ApplicationContext
from algotrader.trading.portfolio import Portfolio
from algotrader.trading.seq_mgr import SequenceManager
from algotrader.utils.ser_deser import JsonSerializer, MapSerializer


def get_default_app_context():
    config = MongoDBConfig()
    persistence_config = PersistenceConfig(None,
                                           DataStore.Mongo, PersistenceMode.Batch,
                                           DataStore.Mongo, PersistenceMode.Batch,
                                           DataStore.Mongo, PersistenceMode.Batch,
                                           DataStore.Mongo, PersistenceMode.Batch)
    app_config = ApplicationConfig(None, None, None, persistence_config,
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


def test_save_orders():
    context = get_default_app_context()

    store = context.provider_mgr.get(DataStore.Mongo)
    store.start()

    ord_mrg = context.order_mgr
    ord_mrg.start()

    order = ord_mrg.send_order(
        NewOrderRequest(cl_id='test_stg', cl_ord_id=1, inst_id=1, portf_id='test_porf', action=OrdAction.BUY,
                        type=OrdType.LIMIT, qty=1000,
                        limit_price=18.5))
    order = ord_mrg.send_order(
        NewOrderRequest(cl_id='test_stg', cl_ord_id=2, inst_id=1, portf_id='test_porf', action=OrdAction.BUY,
                        type=OrdType.LIMIT, qty=1000,
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


def test_save_portfolio():
    print "test_save_portfolio"
    context = get_default_app_context()

    store = context.provider_mgr.get(DataStore.Mongo)
    store.start(app_context=context)

    portf_mgr = context.portf_mgr
    portf_mgr.start(app_context=context)

    p1 = portf_mgr.new_portfolio(portf_id=1, cash=1000)
    p2 = portf_mgr.new_portfolio(portf_id=2, cash=1000)

    before = portf_mgr.get(1)

    portf_mgr.start()
    portf_mgr.stop()

    after = portf_mgr.get(1)
    print "before %s" % before
    print "after %s" % after


def test_save_strategies():
    print "test_save_strategies"
    context = get_default_app_context()

    store = context.provider_mgr.get(DataStore.Mongo)
    store.start(app_context=context)

    stg_mgr = context.stg_mgr
    stg_mgr.start(app_context=context)
    stg_mgr.reset()

    stg1 = stg_mgr.new_stg(trading_config=BacktestingConfig(id='1', stg_id='test1',
                                                            stg_cls='algotrader.strategy.ema_strategy.EMAStrategy'))

    ord_mrg = context.order_mgr
    ord_mrg.start(app_context=context)

    nos = NewOrderRequest(cl_id='test1', cl_ord_id='1', inst_id=1, portf_id='test_porf', action=OrdAction.BUY,
                          type=OrdType.LIMIT, qty=1000,
                          limit_price=18.5)
    order = ord_mrg.send_order(nos)

    stg1.ord_reqs[nos.cl_ord_id] = nos
    stg1.orders[order.cl_ord_id] = order
    stg1.add_position(nos.inst_id, nos.cl_id, nos.cl_ord_id, nos.qty)
    stg1.update_position_price(time=0, inst_id=nos.inst_id, price=100)

    stg2 = stg_mgr.new_stg(trading_config=BacktestingConfig(id='2', stg_id='test2',
                                                            stg_cls='algotrader.strategy.ema_strategy.EMAStrategy'))

    before = stg_mgr.get('test1')

    stg_mgr.stop()

    stg_mgr.start(app_context=context)
    after = stg_mgr.get('test1')
    after.start(app_context=context)

    print "before %s" % MapSerializer.serialize(before)
    print "after %s" % MapSerializer.serialize(after)


def test_save():
    context = get_default_app_context()

    store = context.provider_mgr.get(DataStore.Mongo)
    store.start(app_context=context)

    stg_mgr = context.stg_mgr
    stg_mgr.start(app_context=context)

    portf_mgr = context.portf_mgr
    portf_mgr.start(app_context=context)

    ord_mrg = context.order_mgr
    ord_mrg.start(app_context=context)

    p1 = portf_mgr.new_portfolio(portf_id=1, cash=1000)
    p2 = portf_mgr.new_portfolio(portf_id=2, cash=1000)
    p1.start(app_context=context)
    p2.start(app_context=context)


    stg1 = stg_mgr.new_stg(stg_id='test1', stg_cls='algotrader.strategy.ema_strategy.EMAStrategy')
    stg2 = stg_mgr.new_stg(stg_id='test2', stg_cls='algotrader.strategy.ema_strategy.EMAStrategy')
    stg1.start(app_context=context)
    stg2.start(app_context=context)

    nos = NewOrderRequest(cl_id='test1', cl_ord_id='1', inst_id=1, portf_id='test_porf', action=OrdAction.BUY,
                          type=OrdType.LIMIT, qty=1000,
                          limit_price=18.5)
    order = ord_mrg.send_order(nos)

    stg1.ord_reqs[nos.cl_ord_id] = nos
    stg1.orders[order.cl_ord_id] = order
    stg1.add_position(nos.inst_id, nos.cl_id, nos.cl_ord_id, nos.qty)
    stg1.update_position_price(time=0, inst_id=nos.inst_id, price=100)

    print portf_mgr.get(1)
    print portf_mgr.get(2)


    print stg_mgr.get('test1')
    print stg_mgr.get('test2')

    print ord_mrg.all_orders()


def test_load():
    context = get_default_app_context()

    store = context.provider_mgr.get(DataStore.Mongo)
    store.start(app_context=context)

    stg_mgr = context.stg_mgr
    stg_mgr.start(app_context=context)

    portf_mgr = context.portf_mgr
    portf_mgr.start(app_context=context)

    ord_mrg = context.order_mgr
    ord_mrg.start(app_context=context)

    p1= portf_mgr.get(1)
    p2= portf_mgr.get(2)


    stg1 = stg_mgr.get('test1')
    stg2 = stg_mgr.get('test2')

    p1.start(app_context=context)
    p2.start(app_context=context)
    stg1.start(app_context=context)
    stg2.start(app_context=context)

    print p1
    print p2
    print stg1
    print stg2

    print ord_mrg.all_orders()


def test_save_accounts():
    context = get_default_app_context()
    store = context.provider_mgr.get(DataStore.Mongo)
    store.start(app_context=context)

    acct_mgr = AccountManager(store)
    acct_mgr.start(app_context=context)

    store.start(app_context=context)

    acct1 = acct_mgr.new_account(name="1")
    acct2 = acct_mgr.new_account(name="2")

    before = acct_mgr.all_accounts()

    acct_mgr.save()
    acct_mgr.load()

    after = acct_mgr.all_accounts()

    print before
    print after


def test_save_sequences():
    context = get_default_app_context()
    store = context.provider_mgr.get(DataStore.Mongo)
    store.start(app_context=context)

    seq_mgr = SequenceManager()
    seq_mgr.start(app_context=context)

    print seq_mgr.get_next_sequence("order")
    print seq_mgr.get_next_sequence("order")

    print seq_mgr.get_next_sequence("trade")
    print seq_mgr.get_next_sequence("trade")

    seq_mgr.stop()

    seq_mgr = SequenceManager()
    seq_mgr.start(app_context=context)


test_save_sequences()


test_save_portfolio()

# test_save_strategies()

# test_save()

test_load()
