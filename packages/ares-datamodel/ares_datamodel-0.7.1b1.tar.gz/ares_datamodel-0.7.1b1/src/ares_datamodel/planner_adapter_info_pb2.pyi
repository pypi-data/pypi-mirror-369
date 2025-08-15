from google.protobuf import wrappers_pb2 as _wrappers_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class PlannerAdapterInfo(_message.Message):
    __slots__ = ("unique_id", "adapter_name", "type", "version", "address")
    UNIQUE_ID_FIELD_NUMBER: _ClassVar[int]
    ADAPTER_NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    ADDRESS_FIELD_NUMBER: _ClassVar[int]
    unique_id: _wrappers_pb2.StringValue
    adapter_name: str
    type: str
    version: str
    address: _wrappers_pb2.StringValue
    def __init__(self, unique_id: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., adapter_name: _Optional[str] = ..., type: _Optional[str] = ..., version: _Optional[str] = ..., address: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ...) -> None: ...
