import socket
import select
import sys
import queue
import signal

#
# TCP Echo Server Template Source:
# https://pymotw.com/3/socket/tcp.html
#
# Other references:
# https://pymotw.com/2/select/
#

def error(message):
  print("\n" + message + ".\n")
  sys.exit()


# Make Ctrl-C exit server
signal.signal(signal.SIGINT, signal.SIG_DFL)

# Argument parsing
if (len(sys.argv) != 2):
  error("Argument Error: Arguments must be of the form ttweetser <ServerPort>")
try: server_port = int(sys.argv[1])
except: error("Type Error: <ServerPort> must be of the type int")
if (not 1 <= server_port <= 65535):
  error("Argument Error: <ServerPort> must be between 1 and 65535")


# Create a TCP/IP socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ("localhost", server_port)
print('starting up on {} port {}'.format(*server_address))
server.bind(server_address)

# Listen for incoming connections (5 at once max)
server.listen(5)


# Sockets from which we expect to read
inputs = [server]
# Sockets to which we expect to write
outputs = []
# Outgoing message queues (socket:Queue)
message_queues = {}

# Dictionary of client sockets: usernames
clients = {}
# Dictionary of user: number of hashtags (getusers, tweet)
users = {}
# Dictionary of hashtag: socket of subscribed users (subscribe, unsubscribe)
sockets = {}
# Dictionary of user: list of all tweets from the user (gettweets)
posted_tweets = {}
# Dictionary of user: list of all tweets the user received from the server (timeline)
received_tweets = {}


####################
# Main server loop #
####################
while True:
  # Wait for a connection
  print('waiting for the next event')
  readable, writable, exceptional = select.select(inputs, outputs, inputs)

  # Handle inputs
  for s in readable:
    if s is server:
      # A "readable" server socket is ready to accept a connection
      connection, client_address = s.accept()
      print('new connection from ' + str(client_address))
      connection.setblocking(0)
      inputs.append(connection)
      # Give the connection a queue for data we want to send
      message_queues[connection] = queue.Queue()
    else:
      data = (s.recv(1024)).decode('ascii')
      if data:
        # A readable client socket has data
        print('received ' + data + ' from ' + str(s.getpeername()))

        if data[:2] == 'su': # sendusername
          username = data[2:]
          if username in clients.values():
            print('closing ' + str(client_address) + ' after reading no data')
            # Stop listening for input on the connection
            if s in outputs:
              outputs.remove(s)
            inputs.remove(s)
            s.close()
            # Remove message queue
            del message_queues[s]
            break
          else:
            message_queues[s].put('1')
            clients[s] = username
            print(str(client_address) + '->' + username + ' added to clients')

        if data[:2] == 'tw': # tweet
          print()

        if data[:2] == 'sb': # subscribe
          print()

        if data[:2] == 'ub': # unsubscribe
          print()

        if data == 'ti': # timeline
          print()

        if data == 'gu': # getusers
          message_queues[s].put(str(clients.values()))

        if data == 'gt': # gettweets
          print()

            
        # Add output channel for response
        if s not in outputs:
          outputs.append(s)

        """
        message_queues[s].put(data)
        # Add output channel for response
        if s not in outputs:
            outputs.append(s)
        """
      else:
        # Interpret empty result as closed connection
        print('closing ' + str(client_address) + ' after reading no data')
        # Stop listening for input on the connection
        if s in outputs:
          outputs.remove(s)
        inputs.remove(s)
        del clients[s]
        s.close()
        # Remove message queue
        del message_queues[s]

  # Handle outputs
  for s in writable:
    try:
      next_msg = message_queues[s].get_nowait()
    except queue.Empty:
      # No messages waiting so stop checking for writability.
      print('output queue for ' + str(s.getpeername()) + ' is empty')
      outputs.remove(s)
    else:
      print('sending ' + next_msg + ' to ' + str(s.getpeername()))
      s.send(next_msg.encode('ascii'))

  # Handle "exceptional conditions"
  for s in exceptional:
    print('handling exceptional condition for ' + str(s.getpeername()))
    # Stop listening for input on the connection
    inputs.remove(s)
    if s in outputs:
      outputs.remove(s)
    s.close()
    # Remove message queue
    del message_queues[s]