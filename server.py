import threading
import socket

#Connection
host = '127.0.0.1' #local host
port = 29392

#Starts the server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

#Lists for storing clients and their nicknames
clients = []
nicknames = []

#Broadcast messages from server to all the clients
def broadcast(message):
    for client in clients:
        client.send(message)
        

def handle(client):
    while True:
        try:
            #Broadcasting messages
            #Check if there's any received message from the client, if there are, broadcasts to all the clients/chat room
            message = client.recv(1024)
            broadcast(message)
            
        except:
            #Removing and closing clients
            #If there's error(e.g. user left the chat), removes the connection, its nickname and broadcast that the client has left the chat
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast(f'{nickname} left the chat!'.encode('ascii'))
            nicknames.remove(nickname)
            break

def receive():
    while True:
        #Accepts the connection
        client, address = server.accept()
        print(f"Connected with {str(address)}")

        #Requests for nickname and store inside list
        client.send('NICK'.encode('ascii'))
        nickname = client.recv(1024).decode('ascii')
        nicknames.append(nickname)
        clients.append(client)

        #Broadcasts/prints out the user's nickname to the server
        print(f'Nickname of the client is {nickname}!')
        broadcast(f'{nickname} has joined the chat!'.encode('ascii'))
        client.send('\nConnected to the server! You can now send text messages.'.encode('ascii'))

        #Starts handling thread for client
        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

print('Server is lestening...')
receive()


