import socket
import select
import sys
import re

#
# TCP Echo Client Template Source:
# https://pymotw.com/3/socket/tcp.html
#

def error(message):
  print("\n" + message + "\n")
  sys.exit()


def tweet(input):
  # Check hashtag validity
  hashtag_start = input.find("#")
  hashtags = input[hashtag_start:].split("#")[1:]
  if len(hashtags) > 5: error("hashtag illegal format, connection refused.")
  for hashtag in hashtags:
    if not hashtag.isalnum() or hashtag == "#" or hashtag == "ALL":
      error("hashtag illegal format, connection refused.")

  # Check message validity
  message_start = input.find("\"")
  message_end = input.find("\"", message_start + 1, hashtag_start)
  server_message = input[message_start + 1:message_end]
  if (server_message is None or len(server_message) == 0):
    error("message format illegal.")
  elif (len(server_message) > 150):
    error("message length illegal, connection refused.")

  message = 'tw' + str(hashtags) + server_message

  print('sending ' + message)
  client.send(message.encode('ascii'))


def subscribe(hashtag):
  message = 'sb' + str(hashtag)
  print('sending ' + message)
  client.send(message.encode('ascii'))


def unsubscribe(hashtag):
  message = 'ub' + str(hashtag)
  print('sending ' + message)
  client.send(message.encode('ascii'))


def timeline(tweets):
  for tweet in tweets:
    print(tweet)


def getusers():
  message = 'gu'
  # Send data
  print('sending ' + message)
  client.send(message.encode('ascii'))

  # Look for the response
  data = client.recv(1024).decode('ascii')
  if not data:
    client.close()
  print('recieved ' + data)


def gettweets(input):
  print()


def exitProg():
  print("bye bye")
  client.send(''.encode('ascii'))
  client.close()
  exit()


# Argument parsing
if (len(sys.argv) != 4):
  error("error: args should contain <ServerIP> <ServerPort> <Username>")

server_ip = sys.argv[1]

try: server_port = int(sys.argv[2])
except: error("error: server port invalid, connection refused.")
if (not 1 <= server_port <= 65535):
  error("error: server port invalid, connection refused.")

username = sys.argv[3]
if not re.match("^[A-Za-z0-9]*$", username):
  error("error: username has wrong format, connection refused.")


# Create a TCP/IP socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = (server_ip, server_port)
#print('connecting to {} port {}'.format(*server_address))
try: client.connect(server_address)
except: error("Argument Error: No server found with this <ServerIP> and <ServerPort>")

# Send username to ensure not taken
message = 'su' + username
print('sending ' + message)
client.send(message.encode('ascii'))
# If username taken, send close connection command
if not client.recv(1024).decode('ascii') == '1':
  client.close()
  error('username illegal, connection refused')

# Dict to store timeline
stored_tweets = []

####################
# Main client loop #
####################
while True:

  # Wait for user commands
  user_input = input()

  client.setblocking(0)

  readable, writable, exceptional = select.select([client], [], [], 1)

  for s in readable:
    if s is client:
      message = client.recv(1024).decode('ascii')
      # Add messages to timeline
      pos = 0
      while True:
          new_pos = message.find('\ot', pos + 1)
          if new_pos == -1:
              stored_tweets.append(message[pos+3:])
              print('\'' + message[pos+3:] + '\' added to timeline')
              break
          stored_tweets.append(message[pos+3:new_pos])
          print('\'' + message[pos+3:new_pos] + '\' added to timeline')
          pos = new_pos
          
          

  client.setblocking(1)


  command = user_input.split()[0]
  if command == "tweet":
    tweet(user_input)
  elif command == "subscribe":
    subscribe(user_input.split()[1])
  elif command == "unsubscribe":
    unsubscribe(user_input.split()[1])
  elif command == "timeline":
    timeline(stored_tweets)
  elif command == "getusers":
    print('getting users')
    getusers()
  elif command == "gettweets":
    gettweets(user_input)
  elif command == "exit":
    exitProg()
  else:
    error("illegal command.")
