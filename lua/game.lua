local GrpcServer = require("grpc_server")

local Game = {}

function Game:run()
    local server = GrpcServer:new()
    local i = 0
    while true do
        i = i+1
    --    print ('gaming' .. i)
        server:serve()
    end
end

Game:run()
