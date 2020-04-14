Daniel Bump (@dbump3)
dbump3@gatech.edu
Chieng Chang (@stephanieeechang)
cchang397@gatech.edu

See GitHub page for specific contributions
https://github.com/dbump3/NetworkingPA2/graphs/contributors

CS 3251
4/14/2020
Programming Assignment 2

Files Included
-----------------------------------
ttweetser.py

ttweetcli.py

README.md

Instructions
-----------------------------------
To use the server program:
 1.	Open your terminal at the directory containing ttweetser.py
 2.	To start the server, run the following command: python ttweetser.py <ServerPort>

To use the client program:
 1.	Open your terminal at the directory containing ttweetcli.py
 2.	To start a client, run the following command: python ttweetcli.py <ServerIP> <ServerPort> <Username>

The following commands are supported:
- tweet​ “<150 char max tweet>” <Hashtag>
- subscribe​ <Hashtag>
- unsubscribe​ <Hashtag>
- timeline
- getusers
- gettweets <Username>
- exit

Protocol
-----------------------------------
	When initially parsing the arguments given in the command, the protocol checks that the arguments are of the correct form given the command.
    It also checks that <ServerPort> is an integer in range [1024, 65535], and that <ServerIP> is in IPv4 formats and each unit should be in range [0, 255].
    Then, it tries connecting to the given <ServerIP> and <ServerPort> and, if it cannot connect, throws an error.
	When sending the data from the client to the server, command specific codes will be prepended to the message.
    (Specifically, the following abbreviations: tweet = tw, subscribe = sb, unsubscribe = ub, getusers = gu, gettweets = gt.)
    The server will then recieve the message expecting the prepended codes and know the type of request.
    It will then respond accordingly.

Known Bugs/Limitations
-----------------------------------
- The server can only store messages less than or equal to 150 characters in length
- The server can only manage up to 5 concurrent client connections
- Each client can only subscribe to 3 hashtags
- Requests are processed one at a time
- String '\ot' is used as a deliminator to identify separate tweets in gettweets() ad timeline()
- String ' \end/' is appended to each message the server sends to a client to acknowledge that the complete message has been recieved

Dependent Packages
-----------------------------------
- Python3
- and the following Python3 libraries:
    - queuing
    - select
    - signal
    - socket
    - sys
    - threading

