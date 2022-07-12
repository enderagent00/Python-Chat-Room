
from tkinter.filedialog import *
from tkinter import *
from chatroom_objects import *
from networking import *
from threading import Thread
import socket
import time

'''
ChatRoomClient Class, simple client which handles chat room events and the user interface
'''
class ChatRoomClient(socket.socket, Tk):
    def __init__(self, ip: str, port: int, username: str):
        socket.socket.__init__(self, socket.AF_INET, socket.SOCK_STREAM)
        self.ip = ip
        self.port = port
        self.user = User(username)
        self.users = []
        self.messages = []

        Tk.__init__(self)
        self.title("Chat Room App")
        self.geometry("750x500")
        self.resizable(False, False)
        self.draw_widgets()
        self.configure(background = "#303030")

    '''
    Starts the client
    - Begins attempting to connect to the server
    '''
    def start(self):
        while True:
            try:
                self.connect((self.ip, self.port))
                break
            except:
                time.sleep(2)

        self.send_user()
        Thread(target = self.socket_listener).start()

    '''
    Receives data from the server
    - Function which receives packets from the server and processes them
    - Function only exits once the server disconnects
    '''
    def socket_listener(self):
        while True:
            try:
                packet = DataTransfer.recv_packet(self, 4096)
            except:
                if not DataTransfer.socket_is_connected(self):
                    self.draw_message(Message(SERVER_DISCONNECT_MESSAGE, SYSTEM_USER))
                    self.disable_widgets()
                    break

            if packet["header"] == "users":
                self.users = []

                for user in packet["array"]:
                    self.users.append(User.from_packet(user))

                self.draw_users()
            elif packet["header"] == "messages":
                self.messages = []

                for message in packet["array"]:
                    self.messages.append(Message.from_packet(message))

                self.draw_messages()
            elif packet["header"] == "user-leave":
                user = User.from_packet(packet["user"])
                
                for _user in self.users:
                    if _user.id == user.id:
                        self.users.remove(_user)
                        self.draw_users()
                        break
            elif packet["header"] == "user":
                user = User.from_packet(packet)

                if (packet.get("is-me")):
                    self.user = user
                else:
                    self.users.append(user)

                self.draw_user(user)
            elif packet["header"] == "message":
                message = Message.from_packet(packet)
                self.messages.append(message)
                self.draw_message(message)
            elif packet["header"] == "announcement":
                announcement = Announcement.from_packet(packet)
                self.draw_announcement(announcement)

    '''
    Sends the user for this client to the server
    '''
    def send_user(self):
        packet = self.user.build_packet()
        DataTransfer.send_packet(self, packet)

    '''
    Sends a message to the server
    '''
    def send_message(self, message: Message):
        if self.typebox.get():
            packet = message.build_packet()
            DataTransfer.send_packet(self, packet)

    '''
    Draws a user to the user interface
    '''
    def draw_user(self, user: User):
        self.userbox.insert(END, f"[YOU] {user.name}" if self.user.id == user.id else user.name)

    '''
    Draws a message to the user interface
    '''
    def draw_message(self, message: Message):
        self.chatbox.insert(END, f"[{message.sender.name}]: {message.content}")

    '''
    Draws an announcement to the user interface
    '''
    def draw_announcement(self, announcement: Announcement):
        self.chatbox.insert(END, f"[{SERVER_USER.name}]: {announcement.content}")

    '''
    Draws all of the cached users to the user interface
    '''
    def draw_users(self):
        self.userbox.delete(0, END)
        self.draw_user(self.user)

        for user in self.users:
            self.draw_user(user)

    '''
    Draws all of the cached messages to the user interface
    '''
    def draw_messages(self):
        self.chatbox.delete(0, END)

        for message in self.messages:
            self.draw_message(message)

    '''
    Event which fires when the Enter key is pressed in the typebox
    '''
    def typebox_clicked_enter(self, key: Event):
        message = Message(self.typebox_data.get(), self.user)
        self.send_message(message)
        self.typebox_data.set("")

    '''
    Disables all of the widgets in the user interface
    '''
    def disable_widgets(self):
        self.chatbox.configure(state = DISABLED)
        self.userbox.configure(state = DISABLED)
        self.typebox.configure(state = DISABLED)

    '''
    Draws all of the widgets to the user interface
    '''
    def draw_widgets(self):
        self.typebox_data = StringVar(self)

        self.chatbox = Listbox(self)
        self.chatbox.configure(foreground = "#ffffff", background = "#404040")
        self.chatbox.configure(borderwidth = 0, highlightthickness = 0)
        self.chatbox.configure(font = ("Agency FB", 15))
        self.chatbox.place(x = 10, y = 10, height = 425, width = 600)

        self.userbox = Listbox(self)
        self.userbox.configure(foreground = "#ffffff", background = "#404040")
        self.userbox.configure(borderwidth = 0, highlightthickness = 0)
        self.userbox.configure(font = ("Agency FB", 8))
        self.userbox.configure(justify = CENTER)
        self.userbox.place(x = 625, y = 10, height = 425, width = 110)

        self.typebox = Entry(self, textvariable = self.typebox_data)
        self.typebox.configure(foreground = "#ffffff", background = "#404040")
        self.typebox.configure(borderwidth = 0, highlightthickness = 0)
        self.typebox.configure(font = ("Agency FB", 15))
        self.typebox.configure(justify = CENTER)
        self.typebox.bind("<Return>", self.typebox_clicked_enter)
        self.typebox.place(x = 10, y = 440, height = 50, width = 600)

if __name__ == "__main__":
    username = input("[?] Enter Username: ")

    client = ChatRoomClient(socket.gethostname(), 1024, username)
    client.start()
    client.mainloop()


