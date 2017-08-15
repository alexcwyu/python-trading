import numpy as np
import algotrader.model.time_series2_pb2 as proto

def get_proto_series_data(proto_series: proto.Series):
    if proto_series.dtype == proto.DTFloat:
        data = proto_series.float_data
    if proto_series.dtype == proto.DTDouble:
        data = proto_series.double_data
    if proto_series.dtype == proto.DTInt32:
        data = proto_series.int32_data
    if proto_series.dtype == proto.DTInt64:
        data = proto_series.int64_data
    if proto_series.dtype == proto.DTBool:
        data = proto_series.bool_data
    if proto_series.dtype == proto.DTString:
        data = proto_series.string_data
    if proto_series.dtype == proto.DTByteArray:
        data = proto_series.bytes_data
    return list(data)


def set_proto_series_data(proto_series: proto.Series, data):
    if proto_series.dtype == proto.DTFloat:
        proto_series.float_data.extend(list(data))
    if proto_series.dtype == proto.DTDouble:
        proto_series.double_data.extend(list(data))
    if proto_series.dtype == proto.DTInt32:
        proto_series.int32_data.extend(list(data))
    if proto_series.dtype == proto.DTInt64:
        proto_series.int64_data.extend(list(data))
    if proto_series.dtype == proto.DTBool:
        proto_series.bool_data.extend(list(data))
    if proto_series.dtype == proto.DTString:
        proto_series.string_data.extend(list(data))
    if proto_series.dtype == proto.DTByteArray:
        proto_series.bytes_data.extend(list(data))


def to_np_type(dtype: int) -> np.dtype:
    if dtype == proto.DTFloat:
        return np.float32
    if dtype == proto.DTDouble:
        return np.float64
    if dtype == proto.DTInt32:
        return np.int32
    if dtype == proto.DTInt64:
        return np.int64
    if dtype == proto.DTBool:
        return np.bool_
    if dtype == proto.DTString:
        return np.str_
    if dtype == proto.DTByteArray:
        return np.bytes_


def from_np_type(dtype: np.dtype) -> int:
    if dtype == np.float32:
        return proto.DTFloat
    if dtype == np.float64:
        return proto.DTDouble
    if dtype == np.int32:
        return proto.DTInt32
    if dtype == np.int64:
        return proto.DTInt64
    if dtype == np.bool_:
        return proto.DTBool
    if dtype == np.str_:
        return proto.DTString
    if dtype == np.bytes_:
        return proto.DTByteArray

