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


# Make Ctrl-C exit server
signal.signal(signal.SIGINT, signal.SIG_DFL)

# Argument parsing
if len(sys.argv) != 2:
  error("Argument Error: Arguments must be of the form ttweetser <ServerPort>")
try:
  server_port = int(sys.argv[1])
except:
  error("Type Error: <ServerPort> must be of the type int")
if not 1024 <= server_port <= 65535:
  error("Argument Error: <ServerPort> must be between 1 and 65535")


# Create a TCP/IP socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the socket to the port
server_address = ("127.0.0.1", server_port)
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

# Dictionary of client socket: usernames
clients = {}
# Dictionary of client socket: number of hashtags (getusers, tweet, subscribe, unsubscribe)
users = {}
# Dictionary of hashtag: socket of subscribed users (subscribe, unsubscribe)
sockets = {'ALL':[]}
# Dictionary of client socket: list of all tweets from the user (gettweets)
posted_tweets = {}
# Dictionary of client socket: list of all tweets the user received from the server (timeline)
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
            users[s] = 0
            print(str(client_address) + '->' + username + ' added to clients')
            if s not in outputs:
              outputs.append(s)

        if data[:2] == 'tw': # tweet
          message = data[2:]
          # Parse message + create outgoing tweet for timeline
          tweet = message[message.find(']')+1:]
          out_tweet = '\ot' + clients[s] + ': \"' + tweet + '\" '
          hashtags = message[message.find('['):message.find(']')+1].strip('][').split(', ')
          for i in range(len(hashtags)):
            hashtags[i] = hashtags[i][1:-1]
            out_tweet += '#' + hashtags[i]
          # Add to posted tweets for that user
          if s in posted_tweets.keys():
            posted_tweets[s] += out_tweet
            print(posted_tweets[s])
          else:
            posted_tweets[s] = out_tweet
            print(posted_tweets[s])
          # Send tweet to all subscribed users
          users_sent = []
          for user in sockets["ALL"]:
            if user not in users_sent:
              users_sent.append(user)
              message_queues[user].put(out_tweet)
              if user not in outputs:
                outputs.append(user)
          for hashtag in hashtags:
            if hashtag in sockets.keys():
              for user in sockets[hashtag]:
                if user not in users_sent:
                  users_sent.append(user)
                  message_queues[user].put(out_tweet)
                  if user not in outputs:
                    outputs.append(user)

        if data[:2] == 'sb': # subscribe
          hashtag = data[3:]
          success = True
          if users[s] >= 3:
            success = False
          elif hashtag in sockets.keys() and s not in sockets[hashtag]:
            sockets[hashtag].append(s)
          elif hashtag not in sockets.keys():
            sockets[hashtag] = [s]
          else:
            success = False

          if success:
            users[s] += 1
            message_queues[s].put("operation success")
            if s not in outputs:
              outputs.append(s)
          else:
            message_queues[s].put("operation failed: sub #{} failed, already exists or exceeds 3 limitation".format(hashtag))
            if s not in outputs:
              outputs.append(s)

          print("list of hashtags")
          for ht in sockets.keys():
            un = []
            for sk in sockets[ht]:
              un.append(clients[sk])
            print("#{} has subscribers: {}".format(ht, un))

        if data[:2] == 'ub': # unsubscribe
          hashtag = data[3:]
          success = True
          if hashtag == "ALL":
            for ht in sockets.keys():
              if s in sockets[ht]:
                sockets[ht].remove(s)
          elif hashtag in sockets.keys() and s in sockets[hashtag]:
            sockets[hashtag].remove(s)
          else:
            success = False

          if success:
            users[s] -= 1
            message_queues[s].put("operation success")
            if s not in outputs:
              outputs.append(s)
          else:
            message_queues[s].put("operation failed: unsub #{} failed".format(hashtag))

            if s not in outputs:
              outputs.append(s)

          print("list of hashtags")
          for ht in sockets.keys():
            un = []
            for sk in sockets[ht]:
              un.append(clients[sk])
            print("#{} has subscribers: {}".format(ht, un))

        if data == 'gu': # getusers
          message_queues[s].put('gu' + str(clients.values()))
          if s not in outputs:
            outputs.append(s)

        if data[:2] == 'gt': # gettweets
          # Get socket from username
          message = ''
          username = data[2:]
          try:
            key = next(key for key, val in clients.items() if val == username)
          except:
            message += 'no user ' + username + ' in the system'
          if not message == 'no user ' + username + ' in the system':
            if key not in posted_tweets.keys():
              message += 'no tweets have been posted by ' + username + ' yet'
            # Send reply
            else:
              message += 'gt'
              for val in posted_tweets[key]:
                message += val
            
          message_queues[s].put(message)
          if s not in outputs:
            outputs.append(s)
        

      else:
        # Interpret empty result as closed connection
        print('closing ' + str(client_address) + ' after reading no data')
        # Stop listening for input on the connection
        if s in outputs:
          outputs.remove(s)
        inputs.remove(s)
        del clients[s]
        if s in users.keys(): del users[s]
        for hashtag in sockets.keys():
          if s in sockets[hashtag]:
            new_vals = []
            for val in sockets[hashtag]:
              if not val == s:
                new_vals.append(val)
            del sockets[hashtag]
            for val in new_vals:
              if hashtag in sockets.keys():
                sockets[hashtag] += val
              else:
                sockets[hashtag] = val
        if s in posted_tweets.keys(): del posted_tweets[s]
        if s in received_tweets.keys(): del received_tweets[s]
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