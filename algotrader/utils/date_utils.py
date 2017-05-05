import datetime


class DateUtils:
    epoch = datetime.datetime.fromtimestamp(0)

    @staticmethod
    def datetime_to_unixtimemillis(dt: datetime.datetime) -> int:
        return int((dt - DateUtils.epoch).total_seconds() * 1000)

    @staticmethod
    def unixtimemillis_to_datetime(timestamp: int) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(timestamp / 1000.0)

    @staticmethod
    def datetime_to_timestamp(dt: datetime.datetime) -> int:
        return (dt - DateUtils.epoch).total_seconds()

    @staticmethod
    def timestamp_to_datetime(timestamp: int) -> datetime.datetime:
        return datetime.datetime.fromtimestamp(timestamp)

    @staticmethod
    def datestr_to_unixtimemillis(datestr: str) -> int:
        return int(
            (datetime.datetime.combine(datetime.date(int(datestr[0:4]), int(datestr[4:6]), int(datestr[6:8])),
                                       datetime.datetime.min.time()) - DateUtils.epoch).total_seconds() * 1000)

    @staticmethod
    def date_to_unixtimemillis(d: datetime.date) -> int:
        return int(
            (datetime.datetime.combine(d, datetime.datetime.min.time()) - DateUtils.epoch).total_seconds() * 1000)

    @staticmethod
    def unixtimemillis_to_date(timestamp: int) -> datetime.date:
        return datetime.datetime.fromtimestamp(timestamp / 1000).date()

    @staticmethod
    def date_to_timestamp(d: datetime.date) -> int:
        return (datetime.datetime.combine(d, datetime.datetime.min.time()) - DateUtils.epoch).total_seconds()

    @staticmethod
    def timestamp_to_date(timestamp: int) -> datetime.date:
        return datetime.datetime.fromtimestamp(timestamp).date()
