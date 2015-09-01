#! python2


class NetRef(object):
    __slots__ = ["client", "oid"]
    
    def __init__(self, client, oid):
        self.client = client
        self.oid = oid

    def __getattr__(self, name):
        return self.client.getattr_from_server(self.oid, name)

    def __str__(self):
        return self.oid
