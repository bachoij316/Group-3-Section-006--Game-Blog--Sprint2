import socket
import threading

HOST = '0.0.0.0'
PORT = 8080

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))

server.listen()

clients = []
nicknames = []

#broadcast function 
# sends messages to all the connected clients
def broadcast(message):
    for client in clients:
        client.send(message)


#handle function
# handles the individual connections to the server
def handle(client):
    while True:
        try:
            message = client.recv(1024)
            broadcast(message)
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            nicknames.remove(nickname)
            break



#reciever function
# accepts new connections and listens 
def recieve():
    while True:
        client, address = server.accept()
        print(f"Welcome to the Chat Room {str(address)}!")

        client.send("NICKNAME".encode('utf-8'))
        nickname = clent.recv(1024)
        nicknames.append(nickname)
        client.append(client)

        print(f"Nickname of client is {nickname}")
        broadcast(f"{nickname} has joined the chat.\n".encode('utf-8'))
        client.send("Connected to the chat.".encode('utf-8'))

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()

recieve()