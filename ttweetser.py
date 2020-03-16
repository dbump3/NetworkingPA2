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
        if (len(server_request) > 0): server_mode = server_request[0]
        else: error("Request Error: Invalid request")
        
        # Upload
        if (server_mode == 'u'):
          new_server_message = server_request[1:]
          if (len(new_server_message) > 0):
            server_message = new_server_message
          else:
            server_message = "Empty Message"
        # Download
        elif (server_mode == 'd'):
          print('sending message to the client')
          connection.sendall(bytes(server_message, "utf-8"))
        else:
          error("Request Error: Invalid Request")
        
        print('\nmessage: ' + server_message + '\n')
        connection.close()