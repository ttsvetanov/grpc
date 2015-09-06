#! python2

import connection
import types
import inspect
import sys


local_netref_attrs = frozenset([
    '____conn__', '____oid__', '__class__', '__cmp__', '__del__', '__delattr__',
    '__dir__', '__doc__', '__getattr__', '__getattribute__', '__hash__',
    '__init__', '__metaclass__', '__module__', '__new__', '__reduce__',
    '__reduce_ex__', '__repr__', '__setattr__', '__slots__', '__str__',
    '__weakref__', '__dict__',  '__members__', '__methods__',
    ])

builtin_types = [
    type, object, bool, complex, dict, float, int, list, slice, str, tuple, set, 
    frozenset, Exception, type(None), types.BuiltinFunctionType, types.GeneratorType,
    types.MethodType, types.CodeType, types.FrameType, types.TracebackType, 
    types.ModuleType, types.FunctionType,

    type(int.__add__),      # wrapper_descriptor
    type((1).__add__),      # method-wrapper
    type(iter([])),         # listiterator
    type(iter(())),         # tupleiterator
    type(iter(set())),      # setiterator
]

normalized_builtin_types = dict(((t.__name__, t.__module__), t)
        for t in builtin_types)

class NetRef(object):
    __slots__ = ["____conn__", "____oid__"]
    
    def __init__(self, conn, oid):
        self.____conn__ = conn
        self.____oid__ = oid

    def __getattribute__(self, name):
        if name in local_netref_attrs:
            if name == '__class__' or name == '__doc__':
                return self.__getattr__(name)
            elif name == '__members__' or name == '__dir__':
                return self.__getattr__('__dir__')
            return object.__getattribute__(self, name)
        else:
            return self.__getattr__(name)

    def __getattr__(self, name):
        return self.____conn__.sync_request(connection.ACTION_GETATTR,
                (self.____oid__, name))
        
    def __str__(self):
        return self.____conn__.sync_request(connection.ACTION_STR, self.____oid__)


def class_factory(clsname, modname, methods):
    """Creates a netref class proxying the given class
    
    :param clsname: the class's name
    :param modname: the class's module name
    :param methods: a list of ``(method name, docstring)`` tuples, of the methods
                    that the class defines
    
    :returns: a netref class
    """
    clsname = str(clsname)
    modname = str(modname)
    ns = {"__slots__" : ()}
    for name, doc in methods:
        name = str(name)
        if name not in local_netref_attrs:
            #ns[name] = make_method(name, doc)
            pass
    ns["__module__"] = modname
    if modname in sys.modules and hasattr(sys.modules[modname], clsname):
        ns["__class__"] = getattr(sys.modules[modname], clsname)
    elif (clsname, modname) in normalized_builtin_types:
        ns["__class__"] = normalized_builtin_types[clsname, modname]
    else:
        # to be resolved by the instance
        ns["__class__"] = None
    return type(clsname, (NetRef,), ns)

def inspect_methods(obj):
    """introspects the given (local) object, returning a list of all of its
    methods (going up the MRO).

    :param obj: any local (not proxy) python object

    :returns: a list of ``(method name, docstring)`` tuples of all the methods
              of the given object
    """
    methods = {}
    attrs = {}
    if isinstance(obj, type):
        # don't forget the darn metaclass
        mros = list(reversed(type(obj).__mro__)) + list(reversed(obj.__mro__))
    else:
        mros = reversed(type(obj).__mro__)
    for basecls in mros:
        attrs.update(basecls.__dict__)
    for name, attr in attrs.items():
        if name not in local_netref_attrs and hasattr(attr, "__call__"):
            methods[name] = inspect.getdoc(attr)
    return methods.items()

builtin_classes_cache = {}
for cls in builtin_types:
    builtin_classes_cache[cls.__name__, cls.__module__] = class_factory(
        cls.__name__, cls.__module__, inspect_methods(cls))
