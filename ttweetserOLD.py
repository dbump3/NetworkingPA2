import socket
import sys
import signal

#
# TCP Echo Server Template Source:
# https://pymotw.com/3/socket/tcp.html
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
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ("localhost", server_port)
print('starting up on {} port {}'.format(*server_address))
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

server_message = "Empty Message"

# Dictionary of user: number of hashtags (getusers, tweet)
users = {}
# Dictionary of hashtag: socket of subscribed users (subscribe, unsubscribe)
sockets = {}
# Dictionary of user: list of all tweets from the user (gettweets)
posted_tweets = {}
# Dictionary of user: list of all tweets the user received from the server (timeline)
received_tweets = {}

while True:
  # Wait for a connection
  print('waiting for a connection')
  connection, client_address = sock.accept()

  try:
    print('connection from', client_address)

    # Receive the data in small chunks and retransmit it
    server_request = ""
    while True:
      data = connection.recv(16)
      server_request += '{!r}'.format(data)[2:-1]
      print('received {!r}'.format(data))
      if data:
        print('sending data back to the client')
        connection.sendall(data)
      else:
        print('no data from', client_address)
        break

  finally:
    # Clean up the connection
    if len(server_request) > 0: server_mode = server_request[0]
    else: error("Request Error: Invalid request")

    # Upload
    # if (server_mode == 'u'):
    #   new_server_message = server_request[1:]
    #   if (len(new_server_message) > 0):
    #     server_message = new_server_message
    #   else:
    #     server_message = "Empty Message"
    #   print('\nmessage: ' + server_message + '\n')

    # New User
    if server_mode == 'u':
      username = server_request[1:]
      if username not in users.keys():
        users[username] = 0
        print("user " + username + " logged on to server")
      else: server_message = "error: username already in use"

    # Subscribe to hashtag
    # server_request = s<username> <hashtag> <client_socket>
    elif server_mode == 's':
      username = server_request.split()[0][1:]
      hashtag = server_request.split()[1]
      client_socket = server_request.split()[2]
      if users[username] >= 3:
        error("operation failed: sub " + hashtag + " failed, already exists or exceeds 3 limitation")
      else:
        users[username] += 1
        if hashtag == "#ALL":
          for ht in sockets.keys():
            if client_socket not in sockets[ht]:
              sockets[ht].append(client_socket)
        else:
          if hashtag not in sockets.keys():
              sockets[hashtag] = [client_socket]
          else:
            if client_socket not in sockets[hashtag]:
              sockets[hashtag].append(client_socket)

    # Unsubscribe to hashtag
    # server_request = n<username> <hashtag> <client_socket>
    elif server_mode == 'n':
      username = server_request.split()[0][1:]
      hashtag = server_request.split()[1]
      client_socket = server_request.split()[2]
      users[username] -= 1
      if hashtag == "#ALL":
        for ht in sockets.keys():
          if client_socket in sockets[ht]:
            sockets[ht].remove(client_socket)
      else:
        if client_socket in sockets[hashtag]:
          sockets[hashtag].remove(client_socket)

    # Get users
    elif server_mode == 'g':
      for user in users.keys():
        print(user + "\n")

    # Get tweets
    # server_request = n<username>
    elif server_mode == 't':
      username = server_request.split()[0][1:]
      if username not in posted_tweets.keys():
        print("no user {} in the system".format(username))
      else:
        for tweet in posted_tweets[username]:
          print(tweet + "\n")

    # Download
    elif server_mode == 'd':
      print('sending message to the client')
      connection.sendall(bytes(server_message, "utf-8"))
    else:
      error("Request Error: Invalid Request")
    print('\nmessage: ' + server_message + '\n')

    connection.close()
