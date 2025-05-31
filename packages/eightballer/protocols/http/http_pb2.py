"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
_sym_db = _symbol_database.Default()
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\nnttp.proto\x12\x1baea.eightballer.http.v0_1_0"\x9b\x03\n\x0bHttpMessage\x12P\n\x07request\x18\x05 \x01(\x0b2=.aea.eightballer.http.v0_1_0.HttpMessage.Request_PerformativeH\x00\x12R\n\x08response\x18\x06 \x01(\x0b2>.aea.eightballer.http.v0_1_0.HttpMessage.Response_PerformativeH\x00\x1ac\n\x14Request_Performative\x12\x0e\n\x06method\x18\x01 \x01(\t\x12\x0b\n\x03url\x18\x02 \x01(\t\x12\x0f\n\x07version\x18\x03 \x01(\t\x12\x0f\n\x07headers\x18\x04 \x01(\t\x12\x0c\n\x04body\x18\x05 \x01(\x0c\x1aq\n\x15Response_Performative\x12\x0f\n\x07version\x18\x01 \x01(\t\x12\x13\n\x0bstatus_code\x18\x02 \x01(\x05\x12\x13\n\x0bstatus_text\x18\x03 \x01(\t\x12\x0f\n\x07headers\x18\x04 \x01(\t\x12\x0c\n\x04body\x18\x05 \x01(\x0cB\x0e\n\x0cperformativeb\x06proto3')
_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'http_pb2', _globals)
if not _descriptor._USE_C_DESCRIPTORS:
    DESCRIPTOR._loaded_options = None
    _globals['_HTTPMESSAGE']._serialized_start = 44
    _globals['_HTTPMESSAGE']._serialized_end = 455
    _globals['_HTTPMESSAGE_REQUEST_PERFORMATIVE']._serialized_start = 225
    _globals['_HTTPMESSAGE_REQUEST_PERFORMATIVE']._serialized_end = 324
    _globals['_HTTPMESSAGE_RESPONSE_PERFORMATIVE']._serialized_start = 326
    _globals['_HTTPMESSAGE_RESPONSE_PERFORMATIVE']._serialized_end = 439
