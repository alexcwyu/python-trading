from protobuf3.message import Message
from protobuf3.fields import Int64Field, EnumField, StringField, Int32Field, DoubleField
from enum import Enum


class Bar(Message):

    class Type(Enum):
        Time = 0
        Tick = 1
        Volume = 2
        Dynamic = 3


class Quote(Message):
    pass


class Trade(Message):
    pass


class MarketDepth(Message):

    class Side(Enum):
        Ask = 0
        bid = 1

    class Operation(Enum):
        Insert = 0
        Update = 1
        Delete = 2

Bar.add_field('inst_id', Int64Field(field_number=1, optional=True))
Bar.add_field('type', EnumField(field_number=2, optional=True, enum_cls=Bar.Type))
Bar.add_field('size', Int32Field(field_number=3, optional=True))
Bar.add_field('provider_id', Int32Field(field_number=4, optional=True))
Bar.add_field('timestamp', Int64Field(field_number=5, optional=True))
Bar.add_field('utc_time', Int64Field(field_number=6, optional=True))
Bar.add_field('begin_time', Int64Field(field_number=7, optional=True))
Bar.add_field('open', DoubleField(field_number=9, optional=True))
Bar.add_field('high', DoubleField(field_number=10, optional=True))
Bar.add_field('low', DoubleField(field_number=11, optional=True))
Bar.add_field('close', DoubleField(field_number=12, optional=True))
Bar.add_field('vol', DoubleField(field_number=13, optional=True))
Bar.add_field('adj_close', DoubleField(field_number=14, optional=True))
Bar.add_field('open_int', DoubleField(field_number=15, optional=True))
Quote.add_field('inst_id', Int64Field(field_number=1, optional=True))
Quote.add_field('provider_id', Int32Field(field_number=2, optional=True))
Quote.add_field('timestamp', Int64Field(field_number=3, optional=True))
Quote.add_field('utc_time', Int64Field(field_number=4, optional=True))
Quote.add_field('bid', DoubleField(field_number=5, optional=True))
Quote.add_field('bid_size', Int64Field(field_number=6, optional=True))
Quote.add_field('ask', DoubleField(field_number=7, optional=True))
Quote.add_field('ask_size', Int64Field(field_number=8, optional=True))
Trade.add_field('inst_id', Int64Field(field_number=1, optional=True))
Trade.add_field('provider_id', Int32Field(field_number=2, optional=True))
Trade.add_field('timestamp', Int64Field(field_number=3, optional=True))
Trade.add_field('utc_time', Int64Field(field_number=4, optional=True))
Trade.add_field('price', DoubleField(field_number=5, optional=True))
Trade.add_field('size', Int64Field(field_number=6, optional=True))
MarketDepth.add_field('inst_id', Int64Field(field_number=1, optional=True))
MarketDepth.add_field('provider_id', Int32Field(field_number=2, optional=True))
MarketDepth.add_field('timestamp', Int64Field(field_number=3, optional=True))
MarketDepth.add_field('utc_time', Int64Field(field_number=4, optional=True))
MarketDepth.add_field('provider', StringField(field_number=5, optional=True))
MarketDepth.add_field('position', Int64Field(field_number=6, optional=True))
MarketDepth.add_field('operation', EnumField(field_number=7, optional=True, enum_cls=MarketDepth.Operation))
MarketDepth.add_field('side', EnumField(field_number=8, optional=True, enum_cls=MarketDepth.Side))
MarketDepth.add_field('price', DoubleField(field_number=9, optional=True))
MarketDepth.add_field('size', Int64Field(field_number=10, optional=True))
