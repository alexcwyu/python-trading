from rx.subjects import Subject


class EventBus(object):
    data_subject = Subject()
    order_subject = Subject()
    execution_subject = Subject()
