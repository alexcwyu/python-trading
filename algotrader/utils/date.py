import datetime

epoch = datetime.datetime.fromtimestamp(0)


def datetime_to_unixtimemillis(dt: datetime.datetime) -> int:
    return int((dt - epoch).total_seconds() * 1000)


def unixtimemillis_to_datetime(timestamp: int) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(timestamp / 1000.0)


def datetime_to_timestamp(dt: datetime.datetime) -> int:
    return (dt - epoch).total_seconds()


def timestamp_to_datetime(timestamp: int) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(timestamp)


def datestr_to_unixtimemillis(datestr: str) -> int:
    return int(
        (datetime.datetime.combine(datestr_to_date(datestr),
                                   datetime.datetime.min.time()) - epoch).total_seconds() * 1000)


def datestr_to_date(datestr: str) -> datetime.date:
    return datetime.date(int(datestr[0:4]), int(datestr[4:6]), int(datestr[6:8]))


def date_to_unixtimemillis(d: datetime.date) -> int:
    return int(
        (datetime.datetime.combine(d, datetime.datetime.min.time()) - epoch).total_seconds() * 1000)


def unixtimemillis_to_date(timestamp: int) -> datetime.date:
    return datetime.datetime.fromtimestamp(timestamp / 1000).date()


def date_to_timestamp(d: datetime.date) -> int:
    return (datetime.datetime.combine(d, datetime.datetime.min.time()) - epoch).total_seconds()


def timestamp_to_date(timestamp: int) -> datetime.date:
    return datetime.datetime.fromtimestamp(timestamp).date()
