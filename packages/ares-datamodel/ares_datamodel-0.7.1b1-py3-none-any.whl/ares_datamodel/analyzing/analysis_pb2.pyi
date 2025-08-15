from google.protobuf import wrappers_pb2 as _wrappers_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Analysis(_message.Message):
    __slots__ = ("result", "success", "error_string")
    RESULT_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_STRING_FIELD_NUMBER: _ClassVar[int]
    result: float
    success: bool
    error_string: _wrappers_pb2.StringValue
    def __init__(self, result: _Optional[float] = ..., success: bool = ..., error_string: _Optional[_Union[_wrappers_pb2.StringValue, _Mapping]] = ...) -> None: ...
