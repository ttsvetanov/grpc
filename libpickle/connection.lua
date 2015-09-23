-------------------------------------------------------------------------------
-- this module is just used for server,
-- the features for client is not implemented
-------------------------------------------------------------------------------
local socket = require("socket")
local libpickle = require("libpickle")
local lip = require("lip")
local config = lip.load("../config.ini")
local Connection = {}

local __simple_types = {'nil', 'boolean', 'number', 'string'}
local simple_types = {}
for k, v in pairs(__simple_types) do
    simple_types[v] = true
end

local weak_value_metatbl = {}
weak_value_metatbl.__mode = "v"

local function print_lua_table (lua_table, indent)
	indent = indent or 0
	for k, v in pairs(lua_table) do
		if type(k) == "string" then
			k = string.format("%q", k)
		end
		local szSuffix = ""
		if type(v) == "table" then
			szSuffix = "{"
		end
		local szPrefix = string.rep("    ", indent)
		formatting = szPrefix.."["..k.."]".." = "..szSuffix
		if type(v) == "table" then
			print(formatting)
			print_lua_table(v, indent + 1)
			print(szPrefix.."},")
		else
			local szValue = ""
			if type(v) == "string" then
				szValue = string.format("%q", v)
			else
				szValue = tostring(v)
			end
			print(formatting..szValue..",")
		end
	end
end

function Connection:new(o)
    o = o or {}
    setmetatable(o, self)
    self.__index = self
    o.connected = false
    o.__sock = nil
    o.__local_objects = {}
    o.__oid = 1
    setmetatable(o.__local_objects, weak_value_metatbl)
    return o
end

function Connection:accept(server_sock)
    if not self.connected then
        server_sock:settimeout(2)   -- in seconds
        self.__sock = server_sock:accept()
        if self.__sock ~= nil then
            self.connected = true
            self.__sock:settimeout(1)
            return self.__sock:getpeername()
        end
    end
end

function Connection:shutdown()
    if self.connected then
        self.__sock:shutdown("both")
        self.__sock:close()
        self.connected = false
    end
end

function Connection:send_reply(seq_num, action_type, data)
    local boxed_data = self:__box_reply(data)
    return self:__send(config.msg.reply, seq_num, action_type, boxed_data)
end

function Connection:send_shutdown()
end

function Connection:__send(msg_type, seq_num, action_type, boxed_data)
    if self.connected == false then
        return -1
    end
    local pickled_data = libpickle.dump({msg_type, seq_num, action_type, boxed_data})
    local data_size = string.len(pickled_data)
    if data_size > 99999999 then
        return -1, 'data size is too large'
    end
    self.__sock:send(string.format("%08d", data_size) .. pickled_data)
    return seq_num
end

function Connection:__box_request(obj)
end

function Connection:__box_reply(obj)
    if simple_types[type(obj)] then
        return {config.label.value, obj}
    else
        obj.oid = self.__oid
        self.__oid = self.__oid + 1
        self.__local_objects[obj.oid] = obj
        return {config.label.remote_ref, {obj.oid, tostring(obj), tostring(obj)}}
    end
end

function Connection:recv(timeout)
    if not self.connected then
        return nil
    end
    timeout = timeout or -1
    local recvt, sendt, status = socket.select({self.__sock}, nil, timeout)
    if status == "timeout" then
        return nil
    end
    local pickled_data = ""
    if #recvt then
        local data_size, status = self.__sock:receive(8)
        if status == 'closed' then
            self:shutdown()
            return nil
        end
        if status == 'timeout' and data == nil then
            return nil
        end
        data_size = tonumber(data_size)
        pickled_data, status = self.__sock:receive(data_size)
        if pickled_data == nil then
            return nil
        end
    end

    local package = libpickle.load(pickled_data)
    local msg_type = package[1]
    local seq_num = package[2]
    local action_type = package[3]
    local data = package[4]

    if msg_type == config.msg.request then
        local status, unboxed_data = pcall(self.__unbox, self, data)
        if status == nil then
            -- 'object has been del'
            return nil
        else
            return msg_type, seq_num, action_type, unboxed_data
        end
    end
end

function Connection:__unbox(package)
    local label = package[1]
    local value = package[2]
    if label == config.label.value then
        return value
    elseif label == config.label.tuple or label == config.label.list then
        local res = {}
        for i, v in ipairs(value) do
            res[i] = self:__unbox(v)
        end
        return res
    elseif label == config.label.dict then
        local res = {}
        for i in pairs(value) do
            res[self:__unbox(i)] = self:__unbox(value[i])
        end
        return res
    elseif label == config.label.local_ref then
        return self.__local_objects[value]
    end
end

return Connection
