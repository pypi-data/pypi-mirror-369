"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 6, 31, 1, '', 'analyzing/remote/ares_remote_analyzer_service.proto')
_sym_db = _symbol_database.Default()
from ...analyzing import analysis_pb2 as analyzing_dot_analysis__pb2
from ... import ares_struct_pb2 as ares__struct__pb2
from ...analyzing import analyzer_state_pb2 as analyzing_dot_analyzer__state__pb2
from google.protobuf import empty_pb2 as google_dot_protobuf_dot_empty__pb2
from google.protobuf import wrappers_pb2 as google_dot_protobuf_dot_wrappers__pb2
from ...analyzing import analyzer_capabilities_pb2 as analyzing_dot_analyzer__capabilities__pb2
from ... import ares_data_schema_pb2 as ares__data__schema__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n3analyzing/remote/ares_remote_analyzer_service.proto\x12\x1fares.datamodel.analyzing.remote\x1a\x18analyzing/analysis.proto\x1a\x11ares_struct.proto\x1a\x1eanalyzing/analyzer_state.proto\x1a\x1bgoogle/protobuf/empty.proto\x1a\x1egoogle/protobuf/wrappers.proto\x1a%analyzing/analyzer_capabilities.proto\x1a\x16ares_data_schema.proto"\\\n\x1aParameterValidationRequest\x12>\n\x0cinput_schema\x18\x01 \x01(\x0b2(.ares.datamodel.AresDataSchemaSimplified">\n\x19ParameterValidationResult\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x10\n\x08messages\x18\x02 \x03(\t"k\n\x0fAnalysisRequest\x12*\n\x06inputs\x18\x01 \x01(\x0b2\x1a.ares.datamodel.AresStruct\x12,\n\x08settings\x18\x02 \x01(\x0b2\x1a.ares.datamodel.AresStruct"V\n\x1aAnalysisParametersResponse\x128\n\x10parameter_schema\x18\x01 \x01(\x0b2\x1e.ares.datamodel.AresDataSchema"k\n\x18ConnectionStatusResponse\x12A\n\x06status\x18\x01 \x01(\x0e21.ares.datamodel.analyzing.remote.ConnectionStatus\x12\x0c\n\x04info\x18\x02 \x01(\t"f\n\x15AnalyzerStateResponse\x126\n\x05state\x18\x01 \x01(\x0e2\'.ares.datamodel.analyzing.AnalyzerState\x12\x15\n\rstate_message\x18\x02 \x01(\t"`\n\x0cInfoResponse\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x0f\n\x07version\x18\x02 \x01(\t\x121\n\x0bdescription\x18\x03 \x01(\x0b2\x1c.google.protobuf.StringValue*R\n\x10ConnectionStatus\x12\x1d\n\x19UNKNOWN_CONNECTION_STATUS\x10\x00\x12\r\n\tCONNECTED\x10\x01\x12\x10\n\x0cDISCONNECTED\x10\x022\xf1\x05\n\x19AresRemoteAnalyzerService\x12\x89\x01\n\x0eValidateInputs\x12;.ares.datamodel.analyzing.remote.ParameterValidationRequest\x1a:.ares.datamodel.analyzing.remote.ParameterValidationResult\x12_\n\x07Analyze\x120.ares.datamodel.analyzing.remote.AnalysisRequest\x1a".ares.datamodel.analyzing.Analysis\x12l\n\x15GetAnalysisParameters\x12\x16.google.protobuf.Empty\x1a;.ares.datamodel.analyzing.remote.AnalysisParametersResponse\x12h\n\x13GetConnectionStatus\x12\x16.google.protobuf.Empty\x1a9.ares.datamodel.analyzing.remote.ConnectionStatusResponse\x12Z\n\x08GetState\x12\x16.google.protobuf.Empty\x1a6.ares.datamodel.analyzing.remote.AnalyzerStateResponse\x12P\n\x07GetInfo\x12\x16.google.protobuf.Empty\x1a-.ares.datamodel.analyzing.remote.InfoResponse\x12a\n\x17GetAnalyzerCapabilities\x12\x16.google.protobuf.Empty\x1a..ares.datamodel.analyzing.AnalyzerCapabilitiesb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'analyzing.remote.ares_remote_analyzer_service_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_CONNECTIONSTATUS']._serialized_start = 955
    _globals['_CONNECTIONSTATUS']._serialized_end = 1037
    _globals['_PARAMETERVALIDATIONREQUEST']._serialized_start = 289
    _globals['_PARAMETERVALIDATIONREQUEST']._serialized_end = 381
    _globals['_PARAMETERVALIDATIONRESULT']._serialized_start = 383
    _globals['_PARAMETERVALIDATIONRESULT']._serialized_end = 445
    _globals['_ANALYSISREQUEST']._serialized_start = 447
    _globals['_ANALYSISREQUEST']._serialized_end = 554
    _globals['_ANALYSISPARAMETERSRESPONSE']._serialized_start = 556
    _globals['_ANALYSISPARAMETERSRESPONSE']._serialized_end = 642
    _globals['_CONNECTIONSTATUSRESPONSE']._serialized_start = 644
    _globals['_CONNECTIONSTATUSRESPONSE']._serialized_end = 751
    _globals['_ANALYZERSTATERESPONSE']._serialized_start = 753
    _globals['_ANALYZERSTATERESPONSE']._serialized_end = 855
    _globals['_INFORESPONSE']._serialized_start = 857
    _globals['_INFORESPONSE']._serialized_end = 953
    _globals['_ARESREMOTEANALYZERSERVICE']._serialized_start = 1040
    _globals['_ARESREMOTEANALYZERSERVICE']._serialized_end = 1793