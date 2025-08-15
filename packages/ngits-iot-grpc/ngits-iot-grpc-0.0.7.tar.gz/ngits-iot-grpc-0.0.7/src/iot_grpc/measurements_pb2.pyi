from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MeasurementsRequest(_message.Message):
    __slots__ = ("tenant", "meters", "order_by", "measured_day", "skip", "limit")
    TENANT_FIELD_NUMBER: _ClassVar[int]
    METERS_FIELD_NUMBER: _ClassVar[int]
    ORDER_BY_FIELD_NUMBER: _ClassVar[int]
    MEASURED_DAY_FIELD_NUMBER: _ClassVar[int]
    SKIP_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    tenant: _wrappers_pb2.StringValue
    meters: _containers.RepeatedScalarFieldContainer[str]
    order_by: str
    measured_day: _timestamp_pb2.Timestamp
    skip: int
    limit: int
    def __init__(self, tenant: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., meters: _Optional[_Iterable[str]] = ..., order_by: _Optional[str] = ..., measured_day: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., skip: _Optional[int] = ..., limit: _Optional[int] = ...) -> None: ...

class Measurement(_message.Message):
    __slots__ = ("tenant", "meter_id", "created_ts", "updated_ts", "measured_ts", "value", "media")
    TENANT_FIELD_NUMBER: _ClassVar[int]
    METER_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_TS_FIELD_NUMBER: _ClassVar[int]
    UPDATED_TS_FIELD_NUMBER: _ClassVar[int]
    MEASURED_TS_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    MEDIA_FIELD_NUMBER: _ClassVar[int]
    tenant: str
    meter_id: str
    created_ts: _timestamp_pb2.Timestamp
    updated_ts: _timestamp_pb2.Timestamp
    measured_ts: _timestamp_pb2.Timestamp
    value: float
    media: str
    def __init__(self, tenant: _Optional[str] = ..., meter_id: _Optional[str] = ..., created_ts: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_ts: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., measured_ts: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., value: _Optional[float] = ..., media: _Optional[str] = ...) -> None: ...

class MeasurementsResponse(_message.Message):
    __slots__ = ("measurements", "count", "total_count")
    MEASUREMENTS_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    measurements: _containers.RepeatedCompositeFieldContainer[Measurement]
    count: int
    total_count: int
    def __init__(self, measurements: _Optional[_Iterable[_Union[Measurement, _Mapping]]] = ..., count: _Optional[int] = ..., total_count: _Optional[int] = ...) -> None: ...
