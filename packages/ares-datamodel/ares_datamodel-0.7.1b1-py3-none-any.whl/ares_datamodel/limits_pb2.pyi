from google.protobuf import wrappers_pb2 as _wrappers_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Limits(_message.Message):
    __slots__ = ("unique_id", "minimum", "maximum", "index")
    UNIQUE_ID_FIELD_NUMBER: _ClassVar[int]
    MINIMUM_FIELD_NUMBER: _ClassVar[int]
    MAXIMUM_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    unique_id: _wrappers_pb2.StringValue
    minimum: float
    maximum: float
    index: int
    def __init__(self, unique_id: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ..., minimum: _Optional[float] = ..., maximum: _Optional[float] = ..., index: _Optional[int] = ...) -> None: ...
