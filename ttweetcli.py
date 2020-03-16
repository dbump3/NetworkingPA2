import socket
import sys

#
# TCP Echo Client Template Source:
# https://pymotw.com/3/socket/tcp.html
#

def error(message):
  print("\n" + message + ".\n")
  sys.exit()

# Argument parsing
if (len(sys.argv) < 4):
  error("Argument Error: Arguments must be of the form ttweetcli -u <ServerIP> <ServerPort> \“message\" or ttweetcli –d <ServerIP> <ServerPort>")
server_mode = sys.argv[1]
if ((not (server_mode == "-u" or server_mode == "-d")) or (server_mode == "-u" and not (len(sys.argv) == 5 or len(sys.argv) == 4)) or (server_mode == "-d" and not len(sys.argv) == 4)):
  error("Argument Error: Arguments must be of the form ttweetcli -u <ServerIP> <ServerPort> \“message\" or ttweetcli –d <ServerIP> <ServerPort>")
server_message = ""
if (server_mode == "-u"):
  try: server_message = sys.argv[4]
  except: server_message = ""
  if (len(server_message) > 150):
    error("Argument Error: \"message\" must be 150 characters or less in length")
server_ip = sys.argv[2]
try: server_port = int(sys.argv[3])
except: error("Type Error: <ServerPort> must be of the type int")
if (not 1 <= server_port <= 65535):
  error("Argument Error: <ServerPort> must be between 1 and 65535")


# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = (server_ip, server_port)
#print('connecting to {} port {}'.format(*server_address))
try: sock.connect(server_address)
except: error("Argument Error: No server found with this <ServerIP> and <ServerPort>")

# Upload
if (server_mode == "-u"):
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

# Download
elif (server_mode == "-d"):
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