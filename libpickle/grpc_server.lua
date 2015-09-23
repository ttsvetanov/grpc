local socket = require("socket")
local Connection = require("connection")
local lip = require("lip")
local config = lip.load("../config.ini")

local Server = {}

function Server:new(o)
    o = o or {}
    setmetatable(o, self)
    self.__index = self
    o.__sock = nil
    o.__conn = Connection:new()
    o.test = 1
    return o
end

function Server:shutdown()
    self.__conn:shutdown()
end

function Server:serve_forever()
    self.__sock = socket.tcp()
    self.__sock:bind(config.server.addr, config.server.port)
    self.__sock:listen(1)
    while true do
        client_info = self.__conn:accept(self.__sock)
        if client_info ~= nil then
            print("hello, " .. client_info)
            break
        end
    end
    while self.__conn.connected do
        self:handle_request()
    end
end

function Server:handle_request()
    local conn = self.__conn

    local msg_type, seq_num, action_type, data = conn:recv()
    print(msg_type, seq_num, action_type, data)

    local res = nil
    if msg_type == config.msg.request then
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

        end
    end

    conn:send_reply(seq_num, action_type, res)
end

function Server:__handle_getattr(data)
    local obj = data[1]
    local attr_name = data[2]
    return obj[attr_name]
end

function Server:__handle_setattr(data)
    local obj = data[1]
    local attr_name = data[2]
    local value = data[3]
    obj[attr] = value
end

function Server:__handle_delattr(data)
    local obj = data[1]
    local attr_name = data[2]
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
    return self
end

--return Server
--
-- test

s = Server:new()
s:serve_forever()
