import typing

from abstract import Peer


def parse_config(path='Config.conf') -> typing.Dict[int, Peer]:
    with open(path) as file:
        peers_list: typing.List[Peer] = list(map(lambda l: Peer(*l.split()), file.readlines())) 
        peers = {peer.id: peer for peer in peers_list}
        return peers


SECOND = 1

FOLLOWER_TIMEOUT_RANGE = (0.15 * SECOND, 0.30 * SECOND)
LEADER_TIMEOUT = 0.05 * SECOND
LEADER_TIMEOUT_RANGE = (LEADER_TIMEOUT, LEADER_TIMEOUT)
REQUEST_TIMEOUT = 0.5
