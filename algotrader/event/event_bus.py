from rx.subjects import Subject


class EventBus(object):
    def __init__(self):
        self.data_subject = Subject()
        self.order_subject = Subject()
        self.execution_subject = Subject()
        self.portfolio_subject = Subject()
        self.account_subject = Subject()
