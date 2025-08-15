"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import runtime_version as _runtime_version
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_runtime_version.ValidateProtobufRuntimeVersion(_runtime_version.Domain.PUBLIC, 6, 31, 1, '', 'execution_summary_messages.proto')
_sym_db = _symbol_database.Default()
from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2
from google.protobuf import wrappers_pb2 as google_dot_protobuf_dot_wrappers__pb2
from . import experiment_overview_pb2 as experiment__overview__pb2
from . import device_command_result_pb2 as device__command__result__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n execution_summary_messages.proto\x12\x0eares.datamodel\x1a\x1fgoogle/protobuf/timestamp.proto\x1a\x1egoogle/protobuf/wrappers.proto\x1a\x19experiment_overview.proto\x1a\x1bdevice_command_result.proto"\x8d\x02\n\rExecutionInfo\x12/\n\tunique_id\x18\x01 \x01(\x0b2\x1c.google.protobuf.StringValue\x120\n\x0ctime_started\x18\x02 \x01(\x0b2\x1a.google.protobuf.Timestamp\x121\n\rtime_finished\x18\x03 \x01(\x0b2\x1a.google.protobuf.Timestamp\x12.\n\x08timezone\x18\x04 \x01(\x0b2\x1c.google.protobuf.StringValue\x126\n\x10localtime_offset\x18\x05 \x01(\x0b2\x1c.google.protobuf.StringValue"\xc6\x03\n\x18CampaignExecutionSummary\x12/\n\tunique_id\x18\x01 \x01(\x0b2\x1c.google.protobuf.StringValue\x12\x13\n\x0bcampaign_id\x18\x02 \x01(\t\x12H\n\x14experiment_summaries\x18\x03 \x03(\x0b2*.ares.datamodel.ExperimentExecutionSummary\x125\n\x0eexecution_info\x18\x04 \x01(\x0b2\x1d.ares.datamodel.ExecutionInfo\x12\x15\n\rcampaign_name\x18\x05 \x01(\t\x12\x15\n\rcampaign_tags\x18\x06 \x01(\t\x12\x16\n\x0ecampaign_notes\x18\x07 \x01(\t\x12M\n\x19startup_execution_summary\x18\x08 \x01(\x0b2*.ares.datamodel.ExperimentExecutionSummary\x12N\n\x1acloseout_execution_summary\x18\t \x01(\x0b2*.ares.datamodel.ExperimentExecutionSummary"\xb6\x02\n\x1aExperimentExecutionSummary\x12/\n\tunique_id\x18\x01 \x01(\x0b2\x1c.google.protobuf.StringValue\x12\x15\n\rexperiment_id\x18\x02 \x01(\t\x12<\n\x0estep_summaries\x18\x03 \x03(\x0b2$.ares.datamodel.StepExecutionSummary\x125\n\x0eexecution_info\x18\x04 \x01(\x0b2\x1d.ares.datamodel.ExecutionInfo\x12?\n\x13experiment_overview\x18\x05 \x01(\x0b2".ares.datamodel.ExperimentOverview\x12\x1a\n\x12result_output_path\x18\x06 \x01(\t"\xd3\x01\n\x14StepExecutionSummary\x12/\n\tunique_id\x18\x01 \x01(\x0b2\x1c.google.protobuf.StringValue\x12\x0f\n\x07step_id\x18\x02 \x01(\t\x12B\n\x11command_summaries\x18\x03 \x03(\x0b2\'.ares.datamodel.CommandExecutionSummary\x125\n\x0eexecution_info\x18\x04 \x01(\x0b2\x1d.ares.datamodel.ExecutionInfo"\xfd\x01\n\x17CommandExecutionSummary\x12/\n\tunique_id\x18\x01 \x01(\x0b2\x1c.google.protobuf.StringValue\x12\x12\n\ncommand_id\x18\x02 \x01(\t\x125\n\x0eexecution_info\x18\x03 \x01(\x0b2\x1d.ares.datamodel.ExecutionInfo\x123\n\x06result\x18\x04 \x01(\x0b2#.ares.datamodel.DeviceCommandResult\x12\x14\n\x0ccommand_name\x18\x05 \x01(\t\x12\x1b\n\x13command_description\x18\x06 \x01(\tb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'execution_summary_messages_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_EXECUTIONINFO']._serialized_start = 174
    _globals['_EXECUTIONINFO']._serialized_end = 443
    _globals['_CAMPAIGNEXECUTIONSUMMARY']._serialized_start = 446
    _globals['_CAMPAIGNEXECUTIONSUMMARY']._serialized_end = 900
    _globals['_EXPERIMENTEXECUTIONSUMMARY']._serialized_start = 903
    _globals['_EXPERIMENTEXECUTIONSUMMARY']._serialized_end = 1213
    _globals['_STEPEXECUTIONSUMMARY']._serialized_start = 1216
    _globals['_STEPEXECUTIONSUMMARY']._serialized_end = 1427
    _globals['_COMMANDEXECUTIONSUMMARY']._serialized_start = 1430
    _globals['_COMMANDEXECUTIONSUMMARY']._serialized_end = 1683