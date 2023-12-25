
import socket, threading


HOST_IP = socket.gethostbyname(socket.gethostname())
HOST_PORT = 12345
ENCODER = "utf-8"
BYTESIZE = 1024

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST_IP, HOST_PORT))
server_socket.listen()

client_socket_list = []
client_name_list = []

def broadcast_message(message):
    '''send a message to all clients connected to the server'''
    for client_socket in client_socket_list:
        client_socket.send(message)
    

def recieve_message(client_socket):
    '''recieve an incoming message from a specific client and forward the message to be broadcast'''
    while True:
        try:     
            index = client_socket_list.index(client_socket)
            name = client_name_list[index]
            message = client_socket.recv(BYTESIZE).decode(ENCODER)
            if len(message) == 0:
                continue
            message = f"{name}: {message}".encode(ENCODER)
            broadcast_message(message)
        except: 
            index = client_socket_list.index(client_socket)
            name = client_name_list[index]
            client_socket_list.remove(client_socket)
            client_name_list.remove(name)
            client_socket.close()
            broadcast_message(f"{name} has left the chat".encode(ENCODER))
            break



def connect_client():
    '''connect incoming client to the server'''
    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connected with{client_address}...")

        client_socket.send("NAME".encode(ENCODER))
        client_name = client_socket.recv(BYTESIZE).decode(ENCODER)

        client_socket_list.append(client_socket)
        client_name_list.append(client_name)

        print(f"Name of new client is {client_name}\n")
        client_socket.send(f"{client_name}, you have connected to the server!".encode(ENCODER))
        broadcast_message(f"{client_name} has joined the chat!".encode(ENCODER))

        recieve_message_thread = threading.Thread(target=recieve_message, args=(client_socket,))
        recieve_message_thread.start()

print("Server is listening for incoming connections...\n")
connect_client()

