from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import wrappers_pb2 as _wrappers_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AlertsRequest(_message.Message):
    __slots__ = ("tenant", "ids", "meters", "skip", "limit")
    TENANT_FIELD_NUMBER: _ClassVar[int]
    IDS_FIELD_NUMBER: _ClassVar[int]
    METERS_FIELD_NUMBER: _ClassVar[int]
    SKIP_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    tenant: _wrappers_pb2.StringValue
    ids: _containers.RepeatedScalarFieldContainer[int]
    meters: _containers.RepeatedScalarFieldContainer[str]
    skip: int
    limit: int
    def __init__(self, tenant: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., ids: _Optional[_Iterable[int]] = ..., meters: _Optional[_Iterable[str]] = ..., skip: _Optional[int] = ..., limit: _Optional[int] = ...) -> None: ...

class Alert(_message.Message):
    __slots__ = ("id", "tenant", "meter_id", "created_ts", "updated_ts", "detected_ts", "resolved_ts", "type", "level", "is_active", "details")
    ID_FIELD_NUMBER: _ClassVar[int]
    TENANT_FIELD_NUMBER: _ClassVar[int]
    METER_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_TS_FIELD_NUMBER: _ClassVar[int]
    UPDATED_TS_FIELD_NUMBER: _ClassVar[int]
    DETECTED_TS_FIELD_NUMBER: _ClassVar[int]
    RESOLVED_TS_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    DETAILS_FIELD_NUMBER: _ClassVar[int]
    id: int
    tenant: str
    meter_id: str
    created_ts: _timestamp_pb2.Timestamp
    updated_ts: _timestamp_pb2.Timestamp
    detected_ts: _timestamp_pb2.Timestamp
    resolved_ts: _timestamp_pb2.Timestamp
    type: int
    level: int
    is_active: bool
    details: str
    def __init__(self, id: _Optional[int] = ..., tenant: _Optional[str] = ..., meter_id: _Optional[str] = ..., created_ts: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_ts: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., detected_ts: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., resolved_ts: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., type: _Optional[int] = ..., level: _Optional[int] = ..., is_active: bool = ..., details: _Optional[str] = ...) -> None: ...

class AlertsResponse(_message.Message):
    __slots__ = ("alerts", "count", "total_count")
    ALERTS_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    TOTAL_COUNT_FIELD_NUMBER: _ClassVar[int]
    alerts: _containers.RepeatedCompositeFieldContainer[Alert]
    count: int
    total_count: int
    def __init__(self, alerts: _Optional[_Iterable[_Union[Alert, _Mapping]]] = ..., count: _Optional[int] = ..., total_count: _Optional[int] = ...) -> None: ...
