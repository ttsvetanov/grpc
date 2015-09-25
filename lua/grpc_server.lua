local socket = require("socket")
local Connection = require("connection")
local lip = require("lip")
local pnt = require("print")
local config = lip.load("../config.ini")
config.msg_str = {'Request', 'Reply', 'Exception', 'Shutdown'}
config.action_str = {'getattr', 'setattr', 'delattr', 'str',
            'repr', 'call', 'serverproxy', 'dir', 'cmp', 'hash', 'del', 'contains',
            'delitem', 'getitem', 'iter', 'len', 'setitem', 'next'}

local Modules = {}

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

local Server = {}

function Server:new(o)
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

function Server:foo()
    print 'foo'
    return 'foo'
end

function Server:p(a, b, c, d)
    print(a, b, c, d)
    return 1
end

function Server:shutdown()
    self.__conn:shutdown()
end

function Server:serve()
    -- check new connection request
    local conn = self.__conns[#self.__conns]
    client_info = conn:accept(self.__sock)
    if client_info ~= nil then
        print("hello, " .. client_info)
        table.insert(self.__conns, Connection:new())
    end

    -- handle request
    for k, v in pairs(self.__conns) do
        self:handle_request(v)
    end
end

function Server:handle_request(conn)
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
            print("|", data, table.unpack(data))
        else
            print(data)
        end
        print("--------------------------------------------------------------------")
    end

    local status, res = true, nil
    if msg_type == config.msg.request then
        status, res = pcall(self.__dispatch_request, self, action_type, data)
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

function Server:__dispatch_request(action_type, data)
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
    end
    return res
end

function Server:__handle_getattr(data)
    local obj, attr_name = table.unpack(data)
    return obj[attr_name]
end

function Server:__handle_setattr(data)
    local obj, attr_name, value = table.unpack(data)
    obj[attr] = value
end

function Server:__handle_delattr(data)
    local obj, attr_name = table.unpack(data)
    obj[attr] = nil
end

function Server:__handle_str(data)
    local obj = data
    return tostring(obj)
end

function Server:__handle_repr(data)
    return self:__handle_str(data)
end

function Server:__handle_serverproxy(data)
    print ("__handle_serverproxy")
    return self
end

function Server:__handle_call(data)
    local func, args, kwargs = table.unpack(data)
    print("CallArgs------------------------------------------------------------")
    print("|", table.unpack(args))
    print("--------------------------------------------------------------------")
    local status, res = pcall(func, table.unpack(args))
    if status then
        return res
    else
        error(res)
    end
end

function Server:__handle_dir(data)
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

function Server:__handle_cmp(data)
    local obj, other = table.unpack(data)
    if obj < other then
        return -1
    elseif obj == other then
        return 0
    else
        return 1
    end
end

return Server

-- test
--s = Server:new()
--s:serve_forever()
