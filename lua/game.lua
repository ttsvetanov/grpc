local GrpcServer = require("grpc_server")

local Game = {}

function sleep(n)
    local t0 = os.clock()
    while os.clock() - t0 <= n do end
end

function Game:run()
    local server = GrpcServer:new()
    local i = 0
    while true do
        i = i+1
    --    print ('gaming' .. i)
        server:handle_request()
        sleep(0.1)
    end
end

Game:run()
