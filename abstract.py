import abc
import typing
import dataclasses


@dataclasses.dataclass
class Peer:
    id: int
    host: str
    port: int
    fqdn: str = None
    
    def __post_init__(self):
        self.id = int(self.id)
        self.port = int(self.port)

        self.addr = (self.host, self.port)
        self.fqdn = f'http://{self.host}:{self.port}'
        


class Registerable:
    def register_functions(self, rpc_server):    
        for func in dir(self):
            if callable(getattr(self, func)) and func[0].isupper():
                rpc_server.register_function(getattr(self, func))


class AbstractRaftRPC(abc.ABC):
    @abc.abstractclassmethod
    def RequestVote(self, term: int, candidateId: int) -> typing.Tuple[int, bool]:
        pass

    @abc.abstractclassmethod
    def AppendEntries(self, term: int, leaderId: int) -> typing.Tuple[int, bool]:
        pass

    @abc.abstractclassmethod
    def GetLeader(self) -> typing.Tuple[int, str]:
        pass

    @abc.abstractclassmethod
    def Suspend(self, period: float):
        pass