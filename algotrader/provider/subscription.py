from algotrader.model.model_factory import ModelFactory
from algotrader.utils.market_data_utils import *


class MarketDataSubscriber(object):
    def subscript_market_data(self, feed, instruments, subscription_types, from_date=None, to_date=None):
        for sub_req in self.get_subscription_requests(feed.id(), instruments, subscription_types, from_date, to_date):
            feed.subscribe_mktdata(sub_req)

    def get_subscription_requests(self, feed_id, instruments, subscription_types, from_date=None, to_date=None):
        reqs = []
        for instrument in instruments:
            for subscription_type in subscription_types:
                attrs = subscription_type.split(".")
                md_type = MarketDataSubscriptionType.type(attrs[0])
                provider_id = attrs[1]
                bar_type = BarType.type(attrs[2]) if md_type == MarketDataSubscriptionRequest.Bar else None
                bar_size = BarSize.value(attrs[3]) if md_type == MarketDataSubscriptionRequest.Bar else None

                reqs.append(ModelFactory.build_market_data_subscription_request(type=md_type,
                                                                                inst_id=instrument.inst_id,
                                                                                provider_id=provider_id,
                                                                                bar_type=bar_type,
                                                                                bar_size=bar_size,
                                                                                from_date=from_date,
                                                                                to_date=to_date))
        return reqs
