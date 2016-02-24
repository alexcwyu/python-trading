import pandas as pd
from rx.concurrency import GEventScheduler
from rx.observable import Observable, Observer
from rx.subjects import Subject
import rx
from odo import odo
import blaze
import abc

from algotrader.strategy.strategy import *
from algotrader.provider.feed import *
from algotrader.trading import *

broker_id=Simulator.ID

strategy = Strategy(feed=PandasCSVDataFeed(names=['goog', 'msft']), broker_id=broker_id)

strategy.run()
