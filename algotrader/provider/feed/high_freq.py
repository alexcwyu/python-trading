import csv
import os
import re
from datetime import datetime

import numpy as np
import pandas as pd
from algotrader import Context
from algotrader.model.model_factory import ModelFactory
from algotrader.provider.feed import Feed
from algotrader.utils.date import datestr_to_unixtimemillis, datetime_to_unixtimemillis

# this is a particular parser
def level_one_parser(row, inst_id, provider_id):
    ts = datetime_to_unixtimemillis(datetime.strptime(row[0], '%Y%m%d%H%M%S%f'))
    raw_quote_row = row[1:]

    raw_bid_book = [x for x in raw_quote_row if x[0] == 'B']
    raw_ask_book = [x for x in raw_quote_row if x[0] == 'A']

    bid_split = [re.split('@', x) for x in raw_bid_book]
    bid_flattened = list(map(list, zip(*bid_split)))
    bid_size = np.array([x[1:] for x in bid_flattened[0]], dtype='float')
    bid_array = np.array([x for x in bid_flattened[1]], dtype='float')

    ask_split = [re.split('@', x) for x in raw_ask_book]
    ask_flattened = list(map(list, zip(*ask_split)))
    ask_size = np.array([x[1:] for x in ask_flattened[0]], dtype='float')
    ask_array = np.array([x for x in ask_flattened[1]], dtype='float')

    # TODO review the instrument Id and the idx
    return ModelFactory.build_quote(timestamp=ts,
                                    inst_id=inst_id,
                                    provider_id=provider_id,
                                    bid=bid_array[0], bid_size=bid_size[0],
                                    ask=ask_array[0], ask_size=ask_size[0])


class HighFrequencyFileFeed(Feed):
    dateparse = lambda x: pd.datetime.strptime(x, '%Y-%m-%d')

    def __init__(self):
        super(HighFrequencyFileFeed, self).__init__()

    def _start(self, app_context : Context) -> None:
        self.path = self._get_feed_config("path")

    def id(self):
        return Feed.HF

    def subscribe_mktdata(self, *sub_reqs):
        # self._verify_subscription(*sub_reqs);
        sub_req_ranges = {}
        insts = {}
        for sub_req in sub_reqs:
            insts[sub_req.inst_id] = self.app_context.ref_data_mgr.get_inst(inst_id=sub_req.inst_id)
            sub_req_ranges[sub_req.inst_id] = (
                datestr_to_unixtimemillis(str(sub_req.from_date)), datestr_to_unixtimemillis(str(sub_req.to_date)))

        dfs = self.__load_csv(insts, *sub_reqs)


    def unsubscribe_mktdata(self, *sub_reqs):
        pass

    def __load_csv(self, insts, *sub_reqs):
        dfs = []
        for sub_req in sub_reqs:
            inst = insts[sub_req.inst_id]
            filename = '%s/%s.csv' % (self.path, inst.symbol.lower())
            with open(filename, 'r') as csvfile:
                reader = csv.reader(csvfile, delimiter=' ')
                for row in reader:
                    if row[1][0] == 'B':
                        # TODO:, this call particular parser, generalize it!
                        quote = level_one_parser(row, inst_id=inst.inst_id, provider_id=self.id())
                        self.app_context.event_bus.data_subject.on_next(quote)


