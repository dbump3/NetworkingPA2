Daniel Bump
dbump3@gatech.edu

CS 4641
2/13/2020
Programming Assignment 1

Files Included
-----------------------------------
ttweetser.py - A simple TCP server

ttweetcli.py - A simple TCP client

Sample.txt - An output sample showing the results of running a test scenario
-----------------------------------

Instructions
-----------------------------------
To use the server program:
 1.	Open your terminal at the directory containing ttweetser.py
 2.	To start the server, run the following command: python ttweetser.py <ServerPort>

To use the client program:
 1.	Open your terminal at the directory containing ttweetcli.py
 2.	To upload a message to the server, run the following command: python ttweetcli.py -u <ServerIP> <ServerPort> “message”
	To download a message from the server, run the following command: python ttweetcli.py -d <ServerIP> <ServerPort>
-----------------------------------

Protocol
-----------------------------------
	When initially parsing the arguments given in the command, the protocol checks that the arguments are of the correct form given the command. It also checks that <ServerPort> is an integer between 0 and 65535. If it contains "message," this is checked to ensure that it is a string and 150 characters . Then, it tries connecting to the given <ServerIP> and <ServerPort> and, if it cannot connect, throws an error.
	When sending the data from the client to the server, if it is marked as an upload, it will prepend a u to the message. If it is marked as a download, it will prepend a d to the message. The server will then recieve the message expecting the u or d and know the type of request. It will then respond accordingly.
-----------------------------------

Known Bugs/Limitations
-----------------------------------
- The server can only store messages less than or equal to 150 characters in length
- Requests are processed one at a time
-----------------------------------