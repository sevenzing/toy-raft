from config import parse_config
from raft import Node
import sys
import logging


if __name__ == '__main__':
    id = int(sys.argv[1])

    logging.basicConfig(level=logging.WARNING)
    config = parse_config()
    node_config = config[id]
    config.pop(id)

    node = Node(
        config=node_config,
        peers=config,
    )
    print(f'The server starts at {node.config.fqdn}')
    node.run_server()
