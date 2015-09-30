# GRPC
-------------------------------------------------------------------------------
Remote Procedure Call for Games

# Usage
-------------------------------------------------------------------------------

    import grpc

### Server

Create a server:

    server = grpc.GrpcServer(port)

You can create server with `grpc.GrpcServer()` witch use default configuration.

Add any object you want into the server's field:

    server.game = game_instance

Start the server in the background:

    server.start()

In your game's main loop, let the server handle RPC requests:

    server.handle_request()

Before exit game, call shutdown() to clear the server thread:

    server.shutdown()

### Client

Create a Client:

    client = grpc.GrpcClient()

Connect to the server:

    client.connect((serverIP, serverPort))

Or you can call client.connect() to connect with ('localhost', DEFAULT_PORT)

Now you've got an entry to the server: `client.server_proxy`, you can call
any function that server provided:

    client.server_proxy.test()

Furthermore, you can access any attribute that you gave to the server, and
call their member functions:

    client.server_proxy.game.pause()

Moreover, there is another entry for modules in your game. For example, there
is a "Ferrari" class in file vehicle.py, you can easily add a new ferrari into
your racing game:

    game_proxy = client.server_proxy.game
    game_proxy.new_ferrari = client.server_proxy.modules.vehicle.Ferrari()
    game_proxy.cars.add(game.new_ferrari)

Grpc do this work by proxy server object on client side. You can do local 
operation to the proxy, and it will affect the corresponding server object:

    game_proxy = client.server_proxy.game

    print str(game_proxy)
    print dir(game_proxy)

    some_attr = game_proxy.some_attr
    game_proxy.new_attr = game_proxy.create_new_attr()
    del game_proxy.new_attr

    value1 = game_proxy.some_value1
    value2 = game_proxy.some_value2
    if value1 > value2:
        pass

    dict_proxy = game_proxy.some_dict
    dict_proxy[new_key] = new_value
    print dict_proxy[new_key]
    del dict_proxy[new_key]
    print len(dict_proxy)
    for item in dect_proxy:
        print item

# Note
-------------------------------------------------------------------------------

### Parameters
When client calls a RPC function, the parameters can be:

* all value types that can be pickled, including containers
* proxy object that corresponding to server object
* tuple, list, dict which contains proxy object

If the type of parameter is not supported, the client will raise a TypeError.

### Thread safety
Grpc server handle clients' requests in the main loop (or any game loop that
user called 'server.handle_request()'), not in a independent thread.

It is because the RPC call may access some resource that the main loop is using.
This will cause a thread safe problem, and may crash your game.

### None return call
When client send a call request, it will block and wait for the reply.

Because of the thread safe problem, the Grpc server has to handle the request
in the main thread. It means that the request from client may not be replied
immediately, because the main thread is doing some other things that cost
much time (for example, rendering).

So the user may find the client runs slower then before, here is some methods
to speed up your client:

1. Use object cache instead of get them every time. For example:

    func = client.server_proxy.game.some_func
    for i in range(100):
        func()

is much faster then:

    for i in range(100):
        client.server_proxy.game.some_func()

2. Use None return call
Sometimes we don't care about the return value of the RPC call, so Grpc provide
'None return RPC'. This RPC call return immediately after sent the request,
instead of blocking and waiting for the reply.

    func = client.server_proxy.game.some_func
    for i in range(100):
        func(grpc_need_reply=False)

is much faster then:

    func = client.server_proxy.game.some_func
    for i in range(100):
        func()
