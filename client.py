from rpc import connect


class Client:
    def __init__(self):
        self.fqdn = None
    
    def perform_command(self, command):
        cmd, *args = command.split()
        if cmd in ['connect']:
            host, port = args
            self.fqdn = f'http://{host}:{port}'
            return
        elif cmd in ['suspend']:
            with connect(self.fqdn) as client:
                period = float(args[0])
                return client.Suspend(period)
        elif cmd in ['getleader']:
            with connect(self.fqdn) as client:
                return client.GetLeader()

    def forever_loop(self):
        while 1:
            command = input('\n>')
            if command:
                result = self.perform_command(command)
                if result:
                    print(result)


if __name__ == '__main__':
    try:
        print('The client starts')
        Client().forever_loop()
    except KeyboardInterrupt:
        print('Client is stopping')
