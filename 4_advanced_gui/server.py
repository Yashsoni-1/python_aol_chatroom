import tkinter as TK
import socket
import threading
import json
from tkinter import PhotoImage, StringVar, DISABLED, NORMAL, END, VERTICAL

#Define Window
root = TK.Tk()
root.title("Chat Server")
icon = PhotoImage(file='icons/speech-bubble.png')
root.iconphoto(True, icon)
root.geometry('600x600')
root.resizable(0, 0)

#Fonts
myfont      = ('Simsun', 14)

#Colors
black       = "#010101"
light_green = "#1fc742"
white       = "#ffffff"
red         = "#ff3855"
orange      = "#ffaa1d"
yellow      = "#fff700"
green       = "#1fc742"
blue        = "#5dadec"
purple      = "#9c51b6"

root.config(bg=black)

#Constants
ENCODER  = 'utf-8'
BYTESIZE = 1024


#Connection Class
class Connection:
    '''A class to store a connection - a server socket and pertinent information'''
    def __init__(self) -> None:
        self.host_ip = "192.168.1.5"
        self.encoder = 'utf-8'
        self.bytesize = 1024

        self.client_sockets = []
        self.client_ips = []
        self.banned_ips = []


#Functions
def start_server(connection):
    '''Start the server on a given port number'''
    connection.port = int(port_entry.get())

    #Create Server
    connection.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.server_socket.bind((connection.host_ip, connection.port))
    connection.server_socket.listen()

    #Update GUI
    history_listbox.delete(0, END)
    history_listbox.insert(0, f"Server started on port {connection.port}.")
    end_button.config(state=NORMAL)
    self_broadcast_button.config(state=NORMAL)
    message_button.config(state=NORMAL)
    kick_button.config(state=NORMAL)
    ban_button.config(state=NORMAL)
    start_button.config(state=DISABLED)

    #Start Connect Thread
    connect_thread = threading.Thread(target=connect_client, args=(connection, ))
    connect_thread.start()


def end_server(connection):
    '''Begin the process of ending the server'''
    #Broadcast
    encoded_message = create_enc_message("DISCONNECT", "Admin (broadcasts)", "Server is closing...", light_green)
    broadcast_message(connection, encoded_message)

    #Update GUI
    history_listbox.insert(0, f"Server closing on port {connection.port}.")
    end_button.config(state=DISABLED)
    self_broadcast_button.config(state=DISABLED)
    message_button.config(state=DISABLED)
    kick_button.config(state=DISABLED)
    ban_button.config(state=DISABLED)
    start_button.config(state=NORMAL)

    #Close Server Socket
    connection.server_socket.close()


def connect_client(connection):
    '''Connect an incoming client to the server'''
    while True:
        try:
            client_socket, client_address = connection.server_socket.accept()
            if client_address[0] in connection.banned_ips:
                client_socket.send(create_enc_message("DISCONNECT", "Admin(private)", "You have been banned...goodbye", light_green))
                client_socket.close()
            else:
                client_socket.send(create_enc_message("INFO", "Admin(private)", "Please send your name", light_green))
                message_json = client_socket.recv(connection.bytesize)
                process_message(connection, message_json, client_socket, client_address)
        except:
            break


def create_enc_message(flag, name, message, color):
    '''Return a message packet to be sent'''
    message_packet = {
        "flag": flag,
        "name": name,
        "message": message,
        "color": color
    }

    return json.dumps(message_packet).encode(ENCODER)


def process_message(connection, encoded_message, client_socket, client_address=(0,0)):
    '''Update server information based on a message packet flag'''
    message_packet = json.loads(encoded_message)
    flag    = message_packet["flag"]
    name    = message_packet["name"]
    message = message_packet["message"]
    color   = message_packet["color"]

    if flag == 'INFO':
        #Add
        connection.client_sockets.append(client_socket)
        connection.client_ips.append(client_address[0])

        #Broadcast
        encoded_msg_packet = create_enc_message("MESSAGE", "Admin (broadcast)",
                                                 f"{name} has joined the server!!!", light_green)
        broadcast_message(connection, encoded_msg_packet)

        #Update UI
        client_listbox.insert(END, f"Name: {name}         IP Addr: {client_address[0]}")

        #Start Recvn Thread
        client_recv_thread = threading.Thread(target=recieve_message,
                                               args=(connection, client_socket, ))
        client_recv_thread.start()

    elif flag == 'MESSAGE':
        broadcast_message(connection, encoded_message)
        
        #Update UI
        history_listbox.insert(0, f"{name}: {message}")
        history_listbox.itemconfig(0, fg=color)
    elif flag == "DISCONNECT":
        #Remove/Close Client
        index = connection.client_sockets.index(client_socket)
        connection.client_sockets.remove(client_socket)
        connection.client_ips.pop(index)
        client_listbox.delete(index)
        client_socket.close()

        #Broadcast
        encoded_message = create_enc_message("MESSAGE", "Admin (broadcast)", f"{name} has left the server...", light_green)
        broadcast_message(connection, encoded_message)

        #Update Server UI
        history_listbox.insert(0, f"Admin (broadcast): {name} has left the server...")
        
    else:
        history_listbox.insert(0, "Error processing message...")

    
def broadcast_message(connection, encoded_message):
    '''Send a ENCODED message to all client sockets connected to the server'''
    for client_socket in connection.client_sockets:
        client_socket.send(encoded_message)


def recieve_message(connection, client_socket):
    '''Recieve an incoming message from a client'''
    while True:
       try: 
           encoded_message = client_socket.recv(BYTESIZE)
           process_message(connection, encoded_message, client_socket)
       except:
           break


def self_broadcast(connection):
    '''Broadcast a special admin message to all clients'''
    encoded_message = create_enc_message("MESSAGE", "Admin (broadcast)", input_entry.get(), light_green)
    broadcast_message(connection, encoded_message)

    input_entry.delete(0, END)


def private_message(connection):
    '''Send a private message to a single client'''
    #Select
    index = client_listbox.curselection()[0]
    client_socket = connection.client_sockets[index]

    #Create Msg
    encoded_message = create_enc_message("MESSAGE", "Admin: (Private)", input_entry.get(), light_green)
    client_socket.send(encoded_message)
    input_entry.delete(0, END)


def kick_client(connection):
    '''Kick a given client off the server'''
    #Select
    index = client_listbox.curselection()[0]
    client_socket = connection.client_sockets[index]

    #Create Msg
    encoded_message = create_enc_message("DISCONNECT", "Admin: (Private)", "You have been kicked out...goodbye", light_green)
    history_listbox.insert(0, encoded_message)
    client_socket.send(encoded_message)
    client_listbox.delete(index)
    


def ban_client(connection):
    '''Ban a given client off the server'''
    #Select
    index = client_listbox.curselection()[0]
    client_socket = connection.client_sockets[index]

    #Create Msg
    encoded_message = create_enc_message("MESSAGE", "Admin: (Private)", "You have been banned...", light_green)
    history_listbox.insert(0, encoded_message)
    client_socket.send(encoded_message)
    banned_ip = connection.client_ips[index]
    connection.banned_ips.append(banned_ip)
    


#GUI Layout
#Frames
connection_frame = TK.Frame(root, bg=black)
history_frame    = TK.Frame(root, bg=black)
client_frame     = TK.Frame(root, bg=black)
message_frame    = TK.Frame(root, bg=black)
admin_frame      = TK.Frame(root, bg=black)

connection_frame.pack(pady=5)
history_frame.pack()
client_frame.pack(pady=5)
message_frame.pack()
admin_frame.pack()

#Connection Frame Layout
port_label   = TK.Label( connection_frame, text="Port Number:", font=myfont, bg=black, fg=light_green)
port_entry   = TK.Entry( connection_frame, width=10, borderwidth=3, font=myfont)
start_button = TK.Button(connection_frame, text="Start Server", borderwidth=5,
                          width=15, font=myfont, bg=light_green, command=lambda:start_server(my_connection))
end_button   = TK.Button(connection_frame, text="End Server", borderwidth=5, width=15,
                          font=myfont, bg=light_green, state=DISABLED, command=lambda:end_server(my_connection))

port_label.grid(  row=0, column=0, padx=2, pady=10)
port_entry.grid(  row=0, column=1, padx=2, pady=10)
start_button.grid(row=0, column=2, padx=2, pady=10)
end_button.grid(  row=0, column=3, padx=2, pady=10)

#History Frame Layout
history_scrollbar = TK.Scrollbar(history_frame, orient=VERTICAL)
history_listbox   = TK.Listbox(history_frame, height=10, width=55,
                                borderwidth=3, font=myfont, bg=black, fg=light_green,
                                  yscrollcommand=history_scrollbar.set)
history_scrollbar.config(command=history_listbox.yview)

history_listbox.grid(  row=0, column=0)
history_scrollbar.grid(row=0, column=1, sticky="NS")

#Client Frame Layout
client_scrollbar = TK.Scrollbar(client_frame, orient=VERTICAL)
client_listbox   = TK.Listbox(client_frame, height=10, width=55, borderwidth=3,
                               font=myfont, bg=black, fg=light_green, yscrollcommand=client_scrollbar.set)
client_scrollbar.config(command=client_listbox.yview)

client_listbox.grid(  row=0, column=0)
client_scrollbar.grid(row=0, column=1, sticky="NS")

#Message Frame Layout
input_entry           = TK.Entry(message_frame, width=40, borderwidth=3, font=myfont)
self_broadcast_button = TK.Button(message_frame, text="Broadcast", width=13, borderwidth=5,
                                   font=myfont, bg=light_green, state=DISABLED,
                                     command=lambda:self_broadcast(my_connection))

input_entry.grid(          row=0, column=0, padx=5, pady=5)
self_broadcast_button.grid(row=0, column=1, padx=5, pady=5)

#Admin Frame Layout
message_button = TK.Button(admin_frame, text="PM"  , borderwidth=5, width=15, font=myfont,
                           bg=light_green, state=DISABLED, command=lambda:private_message(my_connection))
kick_button    = TK.Button(admin_frame, text="Kick", borderwidth=5, width=15, font=myfont,
                           bg=light_green, state=DISABLED, command=lambda:kick_client(my_connection))
ban_button     = TK.Button(admin_frame, text="Ban" , borderwidth=5, width=15, font=myfont,
                           bg=light_green, state=DISABLED, command=lambda:ban_client(my_connection))

message_button.grid(row=0, column=0, padx=5, pady=5)
kick_button.grid(   row=0, column=1, padx=5, pady=5)
ban_button.grid(    row=0, column=2, padx=5, pady=5)


#Connection
my_connection = Connection()

#Root Mainloop
root.mainloop()