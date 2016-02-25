# from rx.concurrency import GEventScheduler
# from rx.observable import Observable, Observer
# import rx
from rx.subjects import Subject


class EventBus(object):
    data_subject = Subject()
    order_subject = Subject()
    execution_subject = Subject()
