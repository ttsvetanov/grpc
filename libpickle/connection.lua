-------------------------------------------------------------------------------
-- this module is just used for server,
-- the features for client is not implemented
-------------------------------------------------------------------------------
local socket = require("socket")
local libpickle = require("libpickle")
local Connection = {}

-- MSG_TYPE
local MSG_REQUEST = 1
local MSG_REPLY = 2
local MSG_EXCEPTION = 3
local MSG_SHUTDOWN = 4
local msg_str = ('msg type str', 'request', 'reply', 'exception', 'shutdown')

-- Action_Type
local ACTION_GETATTR = 1
local ACTION_SETATTR = 2
local ACTION_DELATTR = 3
local ACTION_STR = 4
local ACTION_REPR = 5
local ACTION_CALL = 6
local ACTION_GETSERVERPROXY = 7
local ACTION_DIR = 8
local ACTION_CMP = 9
local ACTION_HASH = 10
local ACTION_DEL = 11
local ACTION_CONTAINS = 12
local ACTION_DELITEM = 13
local ACTION_GETITEM = 14
local ACTION_ITER = 15
local ACTION_LEN = 16
local ACTION_SETITEM = 17
local ACTION_NEXT = 18
local action_str = ('action type str', 'getattr', 'setattr', 'delattr', 
        'str', 'repr', 'call', 'server_proxy', 'dir', 'cmp', 'hash', 'del',
        'contains', 'delitem', 'getitem', 'iter', 'len', 'setitem', 'next')

-- obj label
local LABEL_VALUE = 1
local LABEL_TUPLE = 2
local LABEL_LOCAL_REF = 3
local LABEL_REMOTE_REF = 4
local LABEL_NOTIMPLEMENTED = 5
local LABEL_ELLIPSIS = 6
local LABEL_LIST = 7
local LABEL_DICT = 8

local weak_value_metatbl = {}
weak_value_metatbl.__mode = "v"

function Connection:new(o)
    o = o or {}
    setmetatable(o, self)
    self.__index = self
    o.connected = false
    o.__sock = nil
    o.__local_objects = {}
    setmetatable(o.__local_objects, weak_value_metatbl)
    return o
end

function Connection:accept(server_sock)
    if not self.connected then
        server_sock:settimeout(2)   -- in seconds
        self.__sock = server_sock:accept()
        if self.__sock ~= nil then
            self.connected = true
            return self.__sock:getpeername()
        end
    end
end

function Connection:shutdown()
    if self.connected then
        self.__sock:shutdown("both")
        self.__sock:close()
    end
end

function Connection:send_reply(seq_num, action_type, data)
end

function Connection:send_shutdown()
end

function Connection:__send(msg_type, seq_num, action_type, data)
end

function Connection:__box_request(obj)
end

function Connection:__box_reply(obj)
end

function Connection:recv()
end

function Connection:__unbox(package)
end

return Connection
