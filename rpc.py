from xmlrpc.client import ServerProxy
import contextlib
from abstract import AbstractRaftRPC
import typing


@contextlib.contextmanager
def connect(host) -> typing.Iterator[AbstractRaftRPC]:
    with ServerProxy(host, use_builtin_types=True, allow_none=True) as client:
        yield client
