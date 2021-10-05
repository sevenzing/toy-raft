Toy-raft implemetation
===

Task for lab of Distibuted Networks cource of Innopolis university.

> NOTE: This is only raft-election, not the whole protocol


```bash
$ python server.py 0
Server is started at localhost:5000
...
```

```bash
$ python server.py 1
Server is started at localhost:5001
...
```

Servers are ready, one of them should output

```
...
I am a candidate. Term: <term>
Voted for <node id>
Votes received: 1 possible votes
2 node(s) voted for me
I am a leader. Term: <term>
...
```

You can also suspend some servers:
```
$ python client.py
The client starts

> connect localhost 5000

> suspend 10
```
