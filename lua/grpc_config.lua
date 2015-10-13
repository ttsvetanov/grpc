local _msg = {request=1, reply=2, exception=3, shutdown=4}
local _action = {getattr=1, setattr=2, delattr=3, str=4, repr=5, call=6,
serverproxy=7, dir=8, cmp=9, hash=10, delete=11, contains=12,
delitem=13, getitem=14, iter=15, len=16, setitem=17, next=18}
local _label = {value=1, tuple=2, local_ref=3, remote_ref=4, notimplemented=5,
ellipsis=6, list=7, dict=8}
local _server = {addr='localhost', port=10009, buf_size=1024,
log_file='grpc_server_log.txt'}
local _client = {buf_size=1024, log_file='grpc_client_log.txt'}
local _sections = {msg=_msg, action=_action, label=_label, server=_server,
client=_client}

return _sections
