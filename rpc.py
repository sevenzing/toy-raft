import contextlib
import typing
from xmlrpc.client import ServerProxy

from abstract import AbstractRaftRPC


@contextlib.contextmanager
def connect(host) -> typing.Iterator[AbstractRaftRPC]:
    with ServerProxy(host, use_builtin_types=True, allow_none=True) as client:
        yield client
