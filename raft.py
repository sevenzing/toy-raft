import dataclasses

import random
from timer import Timer
import enum
import typing
from abstract import AbstractRaftRPC, Peer, Registerable
import logging
from xmlrpc.server import SimpleXMLRPCServer
import time
from rpc import connect
import socket
import config


class RaftTimer(Timer):
    def restart(self, a, b):
        timeout = random.uniform(a, b)
        return super().restart(timeout)
    

class State(enum.Enum):
    Follower = 0
    Candidate = 1
    Leader = 2


@dataclasses.dataclass(eq=False)
class Node(AbstractRaftRPC, Registerable):
    config: Peer
    peers: typing.Dict[int, Peer] = dataclasses.field(repr=False)
    timer: RaftTimer = dataclasses.field(default_factory=RaftTimer)
    term: int = 0
    current_leader: int = None
    voted_for: int = None
    state: State = State.Follower
    sleep_for: float = None


    def __post_init__(self):
        self.logger = logging.getLogger(f'Node({self.config.port})')

    def restart_timer(self):
        if self.state == State.Leader:
            a, b = config.LEADER_TIMEOUT_RANGE
        else:
            a, b = config.FOLLOWER_TIMEOUT_RANGE
        self.timer.restart(a, b)

        self.logger.debug(f'reset timer {self.timer}')
        

    def run_server(self):
        with SimpleXMLRPCServer(addr=self.config.addr, logRequests=False, use_builtin_types=True) as server:
            self.register_functions(server)
            self.restart_timer()
            self.become_follower()
            
            while True:
                if self.sleep_for is not None:
                    time.sleep(self.sleep_for)
                    self.sleep_for = None
                    self.restart_timer()

                elif not self.timer.is_passed():
                    server.timeout = self.timer.time_left
                    # timer should be updated during execution of a function
                    server.handle_request()

                else:
                    if self.state == State.Follower:
                        print('The leader is dead')
                        self.become_candidate()
                    if self.state == State.Leader:
                        self.ping_all()
                    self.restart_timer()

    def _become(self, state: State):
        self.state = state
        print(f'I am a {self.state.name.lower()}. Term: {self.term}')

    def become_follower(self):
        self._become(State.Follower)

    def become_candidate(self):
        self.term += 1
        self._become(State.Candidate)
        self.restart_timer()

        self.try_become_leader()

    def become_leader(self):
        self.current_leader = self.config.id
        self._become(State.Leader)

    def try_become_leader(self):
        votes_count = self.perform_ellection()
        print(f'{votes_count} node(s) voted for me')
        majority_voted = votes_count > (len(self.peers) + 1) // 2

        if majority_voted:
            self.become_leader()
        else:
            self.become_follower()

    def ping_all(self):
        results = self.broadcast(
            'AppendEntries', 
            timeout=config.REQUEST_TIMEOUT,
            args=(self.term, self.config.id)
            )
        ok = self._check_responses(results)
        if not ok:
            self.become_follower()
    
    def perform_ellection(self) -> bool:
        self.voted_for = self.config.id
        votes_count = 1
        print(f'Voted for {self.voted_for}')

        votes = self.broadcast(
            'RequestVote', 
            timeout=config.REQUEST_TIMEOUT, 
            args=(self.term, self.config.id),
        )
        print(f'Votes received: {len(tuple(filter(None, votes)))} possible votes')
        
        ok = self._check_responses(votes)
        if not ok:
            return votes_count
        else:
            # calculate amount of True in requests, ignor None objects
            votes_count += sum(map(lambda x: int(x[1]), filter(None, votes)))
            return votes_count

    def _check_responses(self, responses) -> bool:
        """
        return True if OK
        """
        for response in filter(None, responses):
            term, _ = response
            if term > self.term:
                self.term = term
                return False
        return True

    def broadcast(self, method_name, timeout, args) -> typing.List[typing.Optional[typing.Tuple[int, bool]]]:
        socket.setdefaulttimeout(timeout)
        results = []
        for peer in self.peers.values():
            with connect(peer.fqdn) as client:
                func = getattr(client, method_name)
                try:
                    result = func(*args)
                except (ConnectionRefusedError, socket.timeout):
                    result = None
                results.append(result)
        socket.setdefaulttimeout(None)
        return results

    def RequestVote(self, term: int, candidateId: int) -> typing.Tuple[int, bool]:
        self.restart_timer()
        if term < self.term:
            voted = False
        else:
            if term > self.term:
                self.term = term
                self.voted_for = None

            if self.voted_for is None:
                voted = True
                self.voted_for = candidateId
            else:
                voted = False
        
        if voted:
            print(f'Voted for node {self.voted_for}')
            self.become_follower()
        
        return self.term, voted

    def AppendEntries(self, term: int, leaderId: int) -> typing.Tuple[int, bool]:
        self.restart_timer()
        if term >= self.term:    
            self.term = term
            if self.current_leader != leaderId:
                self.current_leader = leaderId
                self.become_follower()
            ok = True
        else:
            ok = False
        return self.term, ok

    def GetLeader(self) -> typing.Tuple[int, str]:
        print('Command from client: getleader')
        if self.state == State.Leader:
            result = self.config.id, self.config.fqdn
        else:
            if self.current_leader:
                result = self.current_leader, self.peers[self.current_leader].fqdn
            else:
                result = -1, ""
        print(result)
        return result

    def Suspend(self, period: float):
        print(f'Command from client: suspend {period}')
        self.sleep_for = period
        return True
