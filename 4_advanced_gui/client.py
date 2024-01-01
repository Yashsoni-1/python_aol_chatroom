
import tkinter as TK
import socket
import threading
import json
from tkinter import PhotoImage, StringVar, DISABLED, NORMAL, END

#Define Window
root = TK.Tk()
root.title("Chat Client")
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

class Connection():
    '''A class to store a connection - a client socket and pertinent information'''
    def __init__(self) -> None:
        self.encoder = 'utf-8'
        self.bytesize = 1024


#Functions
def connect(connection):
    '''connect to a server at a given ip/port address'''
    #Clear
    my_listbox.delete(0, END)

    #Get Info
    connection.name      = name_entry.get()
    connection.target_ip = ip_entry.get()
    connection.port      = int(port_entry.get())
    connection.color     = color.get()

    try:
        #Client Socket
        connection.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection.client_socket.connect((connection.target_ip, connection.port))

        #Recv Message
        message_json = connection.client_socket.recv(connection.bytesize)
        process_message(connection, message_json)
    except:
        my_listbox.insert(0, "Connection not established...goodbye")


def disconnect(connection):
    '''Disconnect the client from the server'''
    encoded_message = create_enc_message("DISCONNECT", connection.name, "I am leaving...", connection.color)
    connection.client_socket.send(encoded_message)

    #Update GUI
    gui_end()

def gui_start():
    '''Officially start connection by updating GUI'''
    name_entry.config(       state=DISABLED)
    ip_entry.config(         state=DISABLED)
    port_entry.config(       state=DISABLED)
    connect_button.config(   state=DISABLED)
    disconnect_button.config(state=NORMAL)
    send_button.config(      state=NORMAL)

    for button in color_buttons:
        button.config(state=DISABLED)

def gui_end():
    '''Officially end connection by updating GUI'''
    name_entry.config(       state=NORMAL)
    ip_entry.config(         state=NORMAL)
    port_entry.config(       state=NORMAL)
    connect_button.config(   state=NORMAL)
    disconnect_button.config(state=DISABLED)
    send_button.config(      state=DISABLED)

    for button in color_buttons:
        button.config(state=NORMAL)

def create_enc_message(flag, name, message, color):
    '''Return a message packet to be sent'''
    message_packet = {
        "flag": flag,
        "name": name,
        "message": message,
        "color": color
    }

    return json.dumps(message_packet).encode(ENCODER)

def process_message(connection, encoded_message_json):
    '''Update the client based on message packet flag'''
    #Unpack
    message_packet = json.loads(encoded_message_json)
    flag    = message_packet["flag"]
    name    = message_packet["name"]
    message = message_packet["message"]
    color   = message_packet["color"]

    if flag == "INFO":
        #Send Info
        encoded_message = create_enc_message("INFO", connection.name, "Joins the server!", connection.color)
        connection.client_socket.send(encoded_message)

        #Update GUI
        gui_start()
        recieve_thread = threading.Thread(target=recieve_message, args=(connection,))
        recieve_thread.start()
    elif flag == "MESSAGE":
        #Display Message
        my_listbox.insert(0, f"{name}: {message}")
        my_listbox.itemconfig(0, fg=color)
    elif flag == "DISCONNECT":
        my_listbox.insert(0, f"{name}, {message}")
        my_listbox.itemconfig(0, fg=color)
        disconnect()
    else:
        my_listbox.insert(0, "Error processing the message...")


def send_message(connection):
    '''Send a message to the server'''
            #Cook n Send
    encoded_message = create_enc_message("MESSAGE", connection.name, input_entry.get(), connection.color)
    connection.client_socket.send(encoded_message)

    #Clear Entry
    input_entry.delete(0, END)
        


def recieve_message(connection):
    '''Receive a message from the server'''
    while True:
        try:
            encoded_message_packet = connection.client_socket.recv(connection.bytesize)
            process_message(connection, encoded_message_packet)
        except:
            my_listbox.insert(0, "Connection has been closed...goodbye")
            break
    
#GUI Layout
#Create Frame
info_frame   = TK.Frame(root, bg=black)
color_frame  = TK.Frame(root, bg=black)
output_frame = TK.Frame(root, bg=black)
input_frame  = TK.Frame(root, bg=black)

info_frame.pack()
color_frame.pack()
output_frame.pack(pady=10)
input_frame.pack()


#INFO Frame Layout
name_label = TK.Label(info_frame, text="Client Name:", font=myfont, fg=light_green,
                      bg=black)
name_entry = TK.Entry(info_frame, borderwidth=3, font=myfont)

ip_label   = TK.Label(info_frame, text="Host IP:",font=myfont, fg=light_green,
                      bg=black)

ip_entry   = TK.Entry(info_frame, borderwidth=3,
                         font=myfont)

port_label = TK.Label(info_frame, text="Port Num:",
                           font=myfont, fg=light_green,
                           bg=black)

port_entry = TK.Entry(info_frame, borderwidth=5,
                           font=myfont, width=10)

connect_button = TK.Button(info_frame, text="Connect",
                                font=myfont, bg=light_green,
                                borderwidth=5, width=10,
                                command=lambda:connect(my_connection))

disconnect_button = TK.Button(info_frame, text="Disconnect",
                                   font=myfont, bg=light_green,
                                   borderwidth=5, width=10,
                                   state=DISABLED, command=lambda:disconnect(my_connection))

#Define Frame Layout
name_label.grid(row=0, column=0, padx=2, pady=10)
name_entry.grid(row=0, column=1, padx=2, pady=10)
port_label.grid(row=0, column=2, padx=2, pady=10)
port_entry.grid(row=0, column=3, padx=2, pady=10)
ip_label.grid(  row=1, column=0, padx=2, pady=5)
ip_entry.grid(  row=1, column=1, padx=2, pady=5)
connect_button.grid(   row=1, column=2, padx=4, pady=5)
disconnect_button.grid(row=1, column=3, padx=4, pady=5)

#Color Frame Layout
color = StringVar()
color.set(white)

white_button  = TK.Radiobutton(color_frame, text="White",  variable=color, value=white , bg=black, fg=light_green, font=myfont) 
red_button    = TK.Radiobutton(color_frame, text="Red",    variable=color, value=red   , bg=black, fg=light_green, font=myfont) 
orange_button = TK.Radiobutton(color_frame, text="Orange", variable=color, value=orange, bg=black, fg=light_green, font=myfont) 
yellow_button = TK.Radiobutton(color_frame, text="Yellow", variable=color, value=yellow, bg=black, fg=light_green, font=myfont) 
green_button  = TK.Radiobutton(color_frame, text="Green",  variable=color, value=green , bg=black, fg=light_green, font=myfont) 
blue_button   = TK.Radiobutton(color_frame, text="Blue",   variable=color, value=blue  , bg=black, fg=light_green, font=myfont) 
purple_button = TK.Radiobutton(color_frame, text="Purple", variable=color, value=purple, bg=black, fg=light_green, font=myfont)

color_buttons = [white_button, red_button, orange_button, yellow_button, green_button, blue_button, purple_button]

white_button.grid( row=0, column=3, padx=2, pady=2)
red_button.grid(   row=0, column=4, padx=2, pady=2)
orange_button.grid(row=0, column=5, padx=2, pady=2)
yellow_button.grid(row=0, column=6, padx=2, pady=2)
green_button.grid( row=0, column=7, padx=2, pady=2)
blue_button.grid(  row=0, column=8, padx=2, pady=2)
purple_button.grid(row=0, column=9, padx=2, pady=2)

#Output Frame Layout
my_scrollbar = TK.Scrollbar(output_frame, orient=TK.VERTICAL)
my_listbox   = TK.Listbox(output_frame,
                          height=20, width=55,
                          borderwidth=3, bg=black,
                          fg=light_green, font=myfont,
                          yscrollcommand=my_scrollbar.set)
my_scrollbar.config(command=my_listbox.yview)

my_listbox.grid(  row=0, column=0)
my_scrollbar.grid(row=0, column=1, sticky='NS')


#Input Frame Layout
input_entry = TK.Entry(input_frame, width=45,
                       borderwidth=3, font=myfont)
send_button = TK.Button(input_frame, text="send",
                        borderwidth=5, width=10,
                        font=myfont, bg=light_green,
                        state=DISABLED, command=lambda:send_message(my_connection))
input_entry.grid(row=0, column=0, padx=5, pady=5)
send_button.grid(row=0, column=5, padx=5, pady=5)


#Connection Obj
my_connection = Connection()

#Mainloop
root.mainloop()
