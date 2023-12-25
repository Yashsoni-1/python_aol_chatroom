
import tkinter as TK
import socket
import threading
from tkinter import PhotoImage, StringVar, DISABLED, NORMAL, END

root = TK.Tk()
root.title("Chat Client")
icon = PhotoImage(file='icons/speech-bubble.png')
root.iconphoto(True, icon)
root.geometry('650x650')
root.resizable(0, 0)

myfont = ('Simsun', 14)
black = "#010101"
light_green = "#1fc742"
root.config(bg=black)

ENCODER = 'utf-8'
BYTESIZE = 1024
global client_socket    

def connect():
    '''connect to a server at a given ip/port address'''

    global client_socket
    my_listbox.delete(0, END)

    name = name_entry.get()
    ip = ip_entry.get()
    port = port_entry.get()

    if name and ip and port:
        my_listbox.insert(0, f"{name} is waiting to connect to {ip} at port {port}...")
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ip, int(port)))
        verify_connection(name)
    else:
        my_listbox.insert(0, "Insufficient information for connection...")
    
def verify_connection(name):
    '''verify that the server connection is valid and pass required information'''
    global client_socket

    flag = client_socket.recv(BYTESIZE).decode(ENCODER)

    if flag == 'NAME':
        client_socket.send(name.encode(ENCODER))
        message = client_socket.recv(BYTESIZE).decode(ENCODER)

        if message:
            my_listbox.insert(0, message)

            connect_button.config(state=DISABLED)
            disconnect_button.config(state=NORMAL)
            send_button.config(state=NORMAL)

            name_entry.config(state=DISABLED)
            ip_entry.config(state=DISABLED)
            port_entry.config(state=DISABLED)

            recieve_thread = threading.Thread(target=recieve_message)
            recieve_thread.start()
        else:
            my_listbox.insert(0, "Connection not verified. Goodbye...")
            client_socket.close()
    else:
        my_listbox.insert(0, "Connection refused. Goodbye...")
        client_socket.close()


def disconnect():
    '''disconnect from the server'''
    global client_socket

    client_socket.close()

    connect_button.config(state=NORMAL)
    disconnect_button.config(state=DISABLED)
    send_button.config(state=DISABLED)

    name_entry.config(state=NORMAL)
    ip_entry.config(state=NORMAL)
    port_entry.config(state=NORMAL)


def send_message():
    '''send a message to the server to the broadcast'''
    global client_socket

    message = input_entry.get()
    client_socket.send(message.encode(ENCODER))

    input_entry.delete(0, END)

def recieve_message():
    '''recieve an incoming messsage from the server'''
    global client_socket

    while True:
        try:
            message = client_socket.recv(1024).decode(ENCODER)
            my_listbox.insert(0, message)
        except:
            my_listbox.insert(0, "Closing the connection. Goodbye...")
            disconnect()
            break

info_frame = TK.Frame(root, bg=black)
output_frame = TK.Frame(root, bg=black)
input_frame = TK.Frame(root, bg=black)

info_frame.pack()
output_frame.pack(pady=10)
input_frame.pack()

name_label = TK.Label(info_frame, text="Client Name:",
                      font=myfont, fg=light_green,
                      bg=black)

name_entry = TK.Entry(info_frame, borderwidth=3,
                           font=myfont)

ip_label = TK.Label(info_frame, text="Host IP:",
                         font=myfont, fg=light_green,
                         bg=black)

ip_entry = TK.Entry(info_frame, borderwidth=3,
                         font=myfont)

port_label = TK.Label(info_frame, text="Port:",
                           font=myfont, fg=light_green,
                           bg=black)

port_entry = TK.Entry(info_frame, borderwidth=3,
                           font=myfont, width=12)

connect_button = TK.Button(info_frame, text="Connect",
                                font=myfont, bg=light_green,
                                borderwidth=5, width=10,
                                command=connect)

disconnect_button = TK.Button(info_frame, text="Disconnect",
                                   font=myfont, bg=light_green,
                                   borderwidth=5, width=10,
                                   state=DISABLED, command=disconnect)

name_label.grid(row=0, column=0, padx=2, pady=10)
name_entry.grid(row=0, column=1, padx=2, pady=10)
port_label.grid(row=0, column=2, padx=2, pady=10)
port_entry.grid(row=0, column=3, padx=2, pady=10)
ip_label.grid(row=1, column=0, padx=2, pady=10)
ip_entry.grid(row=1, column=1, padx=2, pady=10)
connect_button.grid(row=1, column=2, padx=4, pady=5)
disconnect_button.grid(row=1, column=3, padx=4, pady=5)

my_scrollbar = TK.Scrollbar(output_frame, orient=TK.VERTICAL)
my_listbox = TK.Listbox(output_frame,
                             height=20, width=55,
                             borderwidth=3, bg=black,
                             fg=light_green, font=myfont,
                             yscrollcommand=my_scrollbar.set)
my_scrollbar.config(command=my_listbox.yview)

my_listbox.grid(row=0, column=0)
my_scrollbar.grid(row=0, column=1, sticky='NS')

input_entry = TK.Entry(input_frame, width=45,
                       borderwidth=3, font=myfont)
send_button = TK.Button(input_frame, text="send",
                        borderwidth=5, width=10,
                        font=myfont, bg=light_green,
                        state=DISABLED, command=send_message)
input_entry.grid(row=0, column=0, padx=5, pady=5)
send_button.grid(row=0, column=5, padx=5, pady=5)


root.mainloop()
