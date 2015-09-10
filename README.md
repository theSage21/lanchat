lanchat
====

[![PyPI](https://badge.fury.io/py/lanchat.svg)](http://badge.fury.io/py/lanchat)

A LAN chatting program in python based on goodwill. It does not need a special
server setup. Install on clients and just run.

Things you should know
----------------------

- No selecting a server( finds it on it's own)
- New server selected if current goes down
- Picks your username from the shell
    - You can change it though
    - ```
         from lanchat import chat
         n = chat.Node()
         n.name='FooBar'
         n.run()
      ```
- Printing is wierd ( Can someone help me fix it?)
- No encryption (boo)
- No protection against DOS


How to use
----------

```
$ pip install lanchat
$ python3 lanchat
```

Install
-------

```
$ virtualenv -p python3 env
$ source enb/bin/activate
$pip install lanchat
```


Run
---

`lanchat`

or

`lanchat --version`
