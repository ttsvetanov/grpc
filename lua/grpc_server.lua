local Connection = require("grpc_connection")
local socket = require("socket")
local config = require("grpc_config")
config.msg_str = {'Request', 'Reply', 'Exception', 'Shutdown'}
config.action_str = {'getattr', 'setattr', 'delattr', 'str',
            'repr', 'call', 'serverproxy', 'dir', 'cmp', 'hash', 'del', 'contains',
            'delitem', 'getitem', 'iter', 'len', 'setitem', 'next'}

local Modules = {}

local unpack = unpack or table.unpack

function Modules:new(o)
    o = o or {}
    setmetatable(o, self)
    self.__index = self.__get_module
    return o
end

function Modules:__get_module(name)
    local status, res = pcall(require, name)
    if status then
        return res
    else
        return "No module " .. name
    end
end

local GrpcServer = {}

function GrpcServer:new(o)
    o = o or {}
    setmetatable(o, self)
    self.__index = self
    o.__conns = {Connection:new()}
    o.test = 1
    o.modules = Modules:new()
    o._G = _G

    o.__sock = socket.tcp()
    o.__sock:bind(config.server.addr, config.server.port)
    o.__sock:listen(5)
    return o
end

function GrpcServer:foo()
    print 'foo'
    error 'error'
    return 'foo'
end

function GrpcServer:p(a, b, c, d)
    print(a, b, c, d)
    return 1
end

function GrpcServer:shutdown()
    self.__conn:shutdown()
end

function GrpcServer:handle_request()
    -- check new connection request
    local conn = self.__conns[#self.__conns]
    local client_info = conn:accept(self.__sock)
    if client_info ~= nil then
        print("hello, " .. client_info)
        table.insert(self.__conns, Connection:new())
    end

    -- handle request
    for k, v in pairs(self.__conns) do
        self:handle_request_for_conn(v)
    end
end

function GrpcServer:handle_request_for_conn(conn)
    if not conn.connected then
        return nil
    end
    local msg_type, seq_num, action_type, data = conn:recv(0)
    if msg_type ~= nil then
        print(config.msg_str[msg_type], seq_num, config.action_str[action_type])
    else
        return nil
    end
    if data ~= nil then
        print('Data--------------------------------------------------------------')
        if type(data) == 'table' then
            print("|", data, unpack(data))
        else
            print(data)
        end
        print("--------------------------------------------------------------------")
    end

    local status, res = true, nil
    if msg_type == config.msg.request then
        local need_reply, data = unpack(data)
        status, res = pcall(self.__dispatch_request, self, action_type, data)
        if not need_reply then
            return nil
        end
    elseif msg_type == config.msg.shutdown then
        print ('Bye, ', conn)
    else
        conn:send_exception(seq_num, 'bad request')
        return nil
    end

    if status == false then
        conn:send_exception(seq_num, res)
    else
        conn:send_reply(seq_num, action_type, res)
    end
end

function GrpcServer:__dispatch_request(action_type, data)
    local res = nil
    if action_type == config.action.getattr then
        res = self:__handle_getattr(data)
    elseif action_type == config.action.setattr then
        res = self:__handle_setattr(data)
    elseif action_type == config.action.delattr then
        res = self:__handle_delattr(data)
    elseif action_type == config.action.str then
        res = self:__handle_str(data)
    elseif action_type == config.action.repr then
        res = self:__handle_repr(data)
    elseif action_type == config.action.serverproxy then
        res = self:__handle_serverproxy(data)
    elseif action_type == config.action.call then
        res = self:__handle_call(data)
    elseif action_type == config.action.getitem then
        res = self:__handle_getitem(data)
    elseif action_type == config.action.setitem then
        res = self:__handle_setitem(data)
    elseif action_type == config.action.delitem then
        res = self:__handle_delitem(data)
    elseif action_type == config.action.dir then
        res = self:__handle_dir(data)
    elseif action_type == config.action.cmp then
        res = self:__handle_cmp(data)
    elseif action_type == config.action.len then
        res = self:__handle_len(data)
    end
    return res
end

function GrpcServer:__handle_getattr(data)
    local obj, attr_name = unpack(data)
    return obj[attr_name]
end

function GrpcServer:__handle_setattr(data)
    local obj, attr_name, value = unpack(data)
    obj[attr_name] = value
end

function GrpcServer:__handle_delattr(data)
    local obj, attr_name = unpack(data)
    obj[attr] = nil
end

function GrpcServer:__handle_str(data)
    local obj = data
    return tostring(obj)
end

function GrpcServer:__handle_repr(data)
    return self:__handle_str(data)
end

function GrpcServer:__handle_serverproxy(data)
    print ("__handle_serverproxy")
    return self
end

function GrpcServer:__handle_call(data)
    local func, args, kwargs = unpack(data)
    print("CallArgs------------------------------------------------------------")
    print("|", unpack(args))
    print("--------------------------------------------------------------------")
    local status, res = pcall(func, unpack(args))
    if status then
        return res
    else
        error(res)
    end
end

function GrpcServer:__handle_getitem(data)
    local obj, key = unpack(data)
    return obj[key]
end

function GrpcServer:__handle_delitem(data)
    local obj, key = unpack(data)
    obj[key] = nil
end

function GrpcServer:__handle_setitem(data)
    local obj, key, value = unpack(data)
    obj[key] = value
end

function GrpcServer:__handle_dir(data)
    local obj = data
    local res = nil
    if type(obj) == 'table' then
        res = {}
        for k, v in pairs(obj) do
            table.insert(res, tostring(k))
        end
    end
    return res
end

function GrpcServer:__handle_cmp(data)
    local obj, other = unpack(data)
    if obj < other then
        return -1
    elseif obj == other then
        return 0
    else
        return 1
    end
end

function GrpcServer:__handle_len(data)
    local obj = data
    return #obj
end

return GrpcServer

-- test
--s = GrpcServer:new()
--s:serve_forever()
