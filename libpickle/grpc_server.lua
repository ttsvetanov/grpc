local socket = require("socket")
local Connection = require("connection")

local Server = {}
local DEFAULT_SERVER_PORT = 10009

function Server:new(o)
    o = o or {}
    setmetatable(o, self)
    self.__index = self
    o.__sock = nil
    o.__conn = Connection:new()
    return o
end

function Server:serve_forever()
    self.__sock = socket.tcp()
    self.__sock:bind('localhost', DEFAULT_SERVER_PORT)
    self.__sock:listen(5)
    while true do
        client_info = self.__conn:accept(self.__sock)
        if client_info ~= nil then
            print("hello, " .. client_info)
            break
        end
    end
end

function Server:shutdown()
    self.__conn:shutdown()
end

return Server
