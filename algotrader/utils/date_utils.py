import datetime


class DateUtils:
    epoch = datetime.datetime.fromtimestamp(0)

    @staticmethod
    def datetime_to_unixtimemillis(dt):
        return int((dt - DateUtils.epoch).total_seconds() * 1000)

    @staticmethod
    def unixtimemillis_to_datetime(timestamp):
        return datetime.datetime.fromtimestamp(timestamp / 1000.0)

    @staticmethod
    def datetime_to_timestamp(dt):
        return (dt - DateUtils.epoch).total_seconds()

    @staticmethod
    def timestamp_to_datetime(timestamp):
        return datetime.datetime.fromtimestamp(timestamp)

    @staticmethod
    def date_to_timestamp(d):
        return (datetime.datetime.combine(d, datetime.datetime.min.time()) - DateUtils.epoch).total_seconds()

    @staticmethod
    def timestamp_to_date(timestamp):
        return datetime.datetime.fromtimestamp(timestamp).date()
