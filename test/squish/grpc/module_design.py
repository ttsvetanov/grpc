# grpc package

# __init__.py 
'''import things'''

# grpc_server.py
class Server:
    '''create SimpleXMLRPCServer
    hold requests, wait for call'''
class Request:
    '''one client request,
    including function name and args'''

# grpc_client.py
class Client:
    '''create connection'''

# grpc_caller.py
class Caller:
    '''caller in update to call rpc,
    user service class derive from it'''
