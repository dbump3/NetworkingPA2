import socket
import sys
import re

#
# TCP Echo Client Template Source:
# https://pymotw.com/3/socket/tcp.html
#


def tweet(input):
  # Check if message is less than 150 characters
  server_message = ""
  try:
    hashtag_start = input.find("#")
    message_start = input.find("\"")
    message_end = input.find("\"", message_start + 1, hashtag_start)
    server_message = input[message_start + 1:message_end]
  except:
    server_message = ""
  if (server_message is None or len(server_message) == 0):
    error("message format illegal.")
  elif (len(server_message) > 150):
    error("message length illegal, connection refused.")

  server_request = bytes('u' + server_message, "utf-8")

  try:
    # Send data
    print('sending {!r}'.format(server_request))
    sock.sendall(server_request)

    # Look for the response
    amount_received = 0
    amount_expected = len(server_request)

    while amount_received < amount_expected:
      data = sock.recv(16)
      amount_received += len(data)
      print('received {!r}'.format(data))

  finally:
    print('upload successful')
    print('closing socket')
    sock.close()


def subscribe(input):
  print()


def unsubscribe(input):
  print()


def timeline():
  print()


def getusers():
  print()


def gettweets(input):
  print()


def exitProg():
  sys.exit()


# send a message to the server
# u : username
# t : tweet
def send(sock, message_type, server_message):
  server_request = bytes(message_type + server_message, "utf-8")

  try:
    # Send data
    print('sending {!r}'.format(server_request))
    sock.sendall(server_request)

    # Look for the response
    amount_received = 0
    amount_expected = len(server_request)

    while amount_received < amount_expected:
      data = sock.recv(16)
      amount_received += len(data)
      print('received {!r}'.format(data))

  finally:
    print('upload successful')
    print('closing socket')
    sock.close()

def error(message):
  print("\n" + message + ".\n")
  sys.exit()

# Argument parsing
if (len(sys.argv) != 4):
  error("error: args should contain <ServerIP> <ServerPort> <Username>")

server_ip = sys.argv[1]

try: server_port = int(sys.argv[2])
except: error("error: server port invalid, connection refused.")
if (not 1 <= server_port <= 65535):
  error("error: server port invalid, connection refused.")

client_username = sys.argv[3]
if not re.match("^[A-Za-z0-9]*$", client_username):
  error("error: username has wrong format, connection refused.")


# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = (server_ip, server_port)
#print('connecting to {} port {}'.format(*server_address))
try: sock.connect(server_address)
except: error("Argument Error: No server found with this <ServerIP> and <ServerPort>")

# Send the username of the client trying to log onto the service to the server
send(sock, 'u', client_username)

# Wait for user commands
user_input = input()
command = user_input.split()[0]
if command == "tweet":
  tweet(user_input)
elif command == "subscribe":
  subscribe(user_input)
elif command == "unsubscribe":
  unsubscribe(user_input)
elif command == "timeline":
  timeline()
elif command == "getusers":
  getusers()
elif command == "gettweets":
  gettweets(user_input)
elif command == "exit":
  exitProg()
else:
  error("illegal command.")

# Download
server_request = bytes('d', "utf-8")

try:
  # Send data
  print('sending {!r}'.format(server_request))
  sock.sendall(server_request)

  # Look for the response
  amount_received = 0
  amount_expected = len(server_request)

  while amount_received < amount_expected:
    data = sock.recv(16)
    amount_received += len(data)
    print('received {!r}'.format(data))

  sock.shutdown(1)

  while True:
    data = sock.recv(16)
    print('received {!r}'.format(data))
    server_message += '{!r}'.format(data)[2:-1]
    if (not data):
      print('no data from', server_address)
      break
finally:
  print('\nmessage: ' + server_message + '\n')
  sock.close()