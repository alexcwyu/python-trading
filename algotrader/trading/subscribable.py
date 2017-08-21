from rx.subjects import Subject
from algotrader.model.time_series2_pb2 import TimeSeriesUpdateEvent

class Subscribable(object):
    def __init__(self, *args, **kwargs):
        self.subject = Subject()

    # TODO: In fact we may not have anything meaningful to push to downstream. Just notify is enough
    def notify_downstream(self, event):
        self.subject.on_next(event)

    def subcribe_upstream(self, observable):
        observable.subject.subscribe(self.on_update)

    def on_update(self, event):
        raise NotImplementedError

