import socket
import select
import sys
import threading

#
# TCP Echo Client Template Source:
# https://pymotw.com/3/socket/tcp.html
#

s_print_lock = threading.Lock()
"""
Thread safe printing
"""
def s_print(*a, **b):
    with s_print_lock:
        print(*a, **b)

def error(message):
  print(message)

def error_exit(message):
  print(message)
  sys.exit()

def tweet(input):
  # Check hashtag validity
  hashtag_start = input.find("#", input.rfind("\""))
  hashtags = input[hashtag_start:].split("#")[1:]
  if len(hashtags) > 5:
    error("hashtag illegal format, connection refused.")
    return
  for hashtag in hashtags:
    if not hashtag.isalnum() or hashtag == "#" or hashtag == "ALL":
      error("hashtag illegal format, connection refused.")
      return

  # Check message validity
  message_start = input.find("\"")
  message_end = input.find("\"", message_start + 1, hashtag_start)
  server_message = input[message_start + 1:message_end]
  if (server_message is None or len(server_message) == 0):
    error("message format illegal.")
    return
  elif (len(server_message) > 150):
    error("message length illegal, connection refused.")
    return

  message = 'tw' + str(hashtags) + server_message

  # print('sending ' + message)
  client.send(message.encode('ascii'))


def subscribe(hashtag):
  message = 'sb' + str(hashtag)
  # Send data
  # print('sending ' + message)
  client.send(message.encode('ascii'))
  # # Look for the response
  # response = client.recv(1024).decode('ascii')
  # if not response:
  #   client.close()
  # print('recieved ' + response)
  # if response == "os":
  #   print("operation success")


def unsubscribe(hashtag):
  message = 'ub' + str(hashtag)
  # Send data
  # print('sending ' + message)
  client.send(message.encode('ascii'))
  # Look for the response
  # response = client.recv(1024).decode('ascii')
  # if not response:
  #   client.close()
  # print('recieved ' + response)
  # if response == "os":
  #   print("operation success")


def timeline(tweets):
  for tweet in tweets:
    print(tweet)


def getusers():
  message = 'gu'
  # Send data
  # print('sending ' + message)
  client.send(message.encode('ascii'))

  # # Look for the response
  # data = client.recv(1024).decode('ascii')
  # if not data:
  #   client.close()
  # print('recieved ' + data)
  # users = data[data.find('['):data.find(']')+1].strip('][').split(', ')
  # for i in range(len(users)):
  #   print(users[i][1:-1])


def gettweets(input):
  message = 'gt' + input
  # Send data
  # print('sending ' + message)
  client.send(message.encode('ascii'))

  # Look for the response
  # data = client.recv(1024).decode('ascii')
  # if not data:
  #   client.close()
  # print('recieved ' + data)
  #
  # tweets = data[data.find('['):data.find(']')+1].strip('][').split(', ')
  # for i in range(len(tweets)):
  #   print(tweets[i][1:-1])
  #
  # if data == 'no':
  #   print('no user ' + input + ' in the system')
  # elif data == 'nt':
  #     print('no tweets have been posted by ' + input + ' yet')
  # else:
  #   pos = 0
  #   while True:
  #     new_pos = data.find('\ot', pos + 1)
  #     if new_pos == -1:
  #       print(data[pos+3:])
  #       break
  #     print(data[pos+3:new_pos])
  #     pos = new_pos


def exitProg():
  print("bye bye")
  client.send(''.encode('ascii'))
  client.close()
  recv_thread.join()
  exit()


def recvall(sock):
  # Helper function to recv n bytes or return None if EOF is hit
  data = bytearray()
  # while len(data) < n:
  #   packet = sock.recv(n - len(data))
  while True:
    packet = sock.recv(1024)
    if not packet:
      return None
    data.extend(packet)
    if bytes(' \end/', encoding='ascii') in data:
      return data[:-6]


def serverRecv():
  while True:
    try:
      readable, writable, exceptional = select.select([client], [], [], 1)
    except:
      break

    for s in readable:
      if s is client:
        try:
          message = recvall(client).decode('ascii')
          if message == '':
            s_print("Error: Server offline. Exiting.")
            return
        except:
          break
        if message[:3] == '\ot':
          # Add messages to timeline and print received tweets
          pos = 0
          while True:
            new_pos = message.find('\ot', pos + 1)
            if new_pos == -1:
              stored_tweets.append(message[pos+3:])
              colon = message.find(':')
              # print received tweet
              s_print(message[pos+3:colon] + message[colon + 1:])
              # s_print('\'' + message[pos+3:] + '\' added to timeline')
              break
            stored_tweets.append(message[pos+3:new_pos])
            # print received tweet
            s_print(message[pos + 3:new_pos])
            # s_print('\'' + message[pos+3:new_pos] + '\' added to timeline')
            pos = new_pos
        # gettweets
        elif message[:2] == 'gt':
          message = message[2:]
          tweets = message.split('\ot')
          for t in tweets:
            if len(t) > 0:
              s_print(t)
          # pos = 0
          # while True:
          #   new_pos = message.find('\ot', pos + 1)
          #   if new_pos == -1:
          #     if len(message[pos + 3:]) > 0:
          #       # print("message 1: ")
          #       print(message[pos + 3:])
          #     break
          #   else:
          #     if len(message[pos + 3:new_pos]) > 0:
          #       # print("message 2: ")
          #       print(message[pos + 3:new_pos])
          #   pos = new_pos
        # getusers
        elif message[:2] == 'gu':
          message = message[2:]
          users = message[message.find('['):message.find(']') + 1].strip('][').split(', ')
          for i in range(len(users)):
            s_print(users[i][1:-1])
        else:
          s_print(message)


# Argument parsing
if len(sys.argv) != 4:
  error_exit("error: args should contain <ServerIP>   <ServerPort>   <Username>")

server_ip = sys.argv[1]
if (server_ip == 'localhost' or  server_ip == '::1'): server_ip = '127.0.0.1'
ip = server_ip.split('.')
if len(ip) != 4:
  error_exit("error: server ip invalid, connection refused.")
for num in ip:
  num = int(num)
  if num < 0 or num > 255:
    error_exit("error: server ip invalid, connection refused.")

try: server_port = int(sys.argv[2])
except: error_exit("error: server port invalid, connection refused.")
if not 1024 <= server_port <= 65535:
  error_exit("error: server port invalid, connection refused.")

username = sys.argv[3]
if not username.isalnum():
  error_exit("error: username has wrong format, connection refused.")


# Create a TCP/IP socket
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port where the server is listening
server_address = (server_ip, server_port)
#print('connecting to {} port {}'.format(*server_address))
try: client.connect(server_address)
except: error_exit("connection error, please check your server: Connection refused")

# Send username to ensure not taken
message = 'su' + username
# print('sending ' + message)
client.send(message.encode('ascii'))
# If username taken, send close connection command
if not recvall(client).decode('ascii') == '1':
  client.close()
  error_exit("error: username has wrong format, connection refused.")

# Connection successfully established
print("username legal, connection established.")

# Dict to store timeline
stored_tweets = []

# Start server receiving thread
recv_thread = threading.Thread(target=serverRecv)
recv_thread.daemon = True
recv_thread.start()

####################
# Main client loop #
####################
while True:

  # Wait for user commands
  user_input = input()

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
    getusers()
  elif command == "gettweets":
    gettweets(user_input.split()[1])
  elif command == "exit":
    exitProg()
  else:
    error("illegal command.")
