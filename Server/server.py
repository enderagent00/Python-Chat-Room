
from chatroom_objects import *
from networking import *
from threading import Thread
import socket

'''
ChatRoomServer Class, simple server which handles chat room events
'''
class ChatRoomServer(socket.socket):
    def __init__(self, ip: str, port: int):
        super().__init__(socket.AF_INET, socket.SOCK_STREAM)
        self.bind((ip, port))
        self.listen(5)

        self.ip = ip
        self.port = port
        self.clients = []
        self.messages = []
        self.attachments = {}

        self.validate_user = lambda user: len(user.name) < 16
        self.validate_message = lambda message: len(message.content) < 128

    '''
    Starts the server
    - Begins listening for clients and opens a new thread when one connects
    '''
    def start(self):
        while True:
            conn, addr = self.accept()
            client = Client(addr[0], addr[1], conn)
            self.clients.append(client)

            Thread(target = self.socket_listener, args = (client,)).start()

    '''
    Receives data from a single client
    - Function which receives packets from a client and processes them
    - Each client is supposed to have their own thread running like this
    - Thread exits automatically once the client disconnects
    '''
    def socket_listener(self, client: Client):
        while True:
            try:
                packet = DataTransfer.recv_packet(client, 4096)
            except:
                if not DataTransfer.socket_is_connected(client.sock):
                    self.clients.remove(client)
                    self.broadcast_leave(client.user)
                    self.broadcast_announcement(Announcement(f"{client.user.name} Has Left"))
                    break

            if packet["header"] == "user":
                user = User.from_packet(packet)
                client.received_user = True

                if self.validate_user(user):
                    user.id = ObjectIDGenerator.generate_id()
                    client.user = user
                    self.broadcast_user(user)
                    self.broadcast_announcement(Announcement(f"{user.name} Has Joined"))

                    if len(self.clients) > 1:
                        self.send_users(client)

                    if len(self.messages):
                        self.send_messages(client)
            elif packet["header"] == "message":
                message = Message.from_packet(packet)

                if self.validate_message(message):
                    message.id = ObjectIDGenerator.generate_id()
                    self.messages.append(message)
                    self.broadcast_message(message)

    '''
    Tells all clients that a new user has connected
    - packet["is-me"] becomes true if the client being sent the packet is the new user
    '''
    def broadcast_user(self, user: User):
        for client in self.clients:
            packet = user.build_packet()

            if client.user.id == user.id:
                packet["is-me"] = True

            DataTransfer.send_packet(client, packet)

    '''
    Tells all clients that a new message has been sent
    '''
    def broadcast_message(self, message: Message):
        packet = message.build_packet()

        for client in self.clients:
            DataTransfer.send_packet(client, packet)

    '''
    Tells all clients that a client has disconnected
    '''
    def broadcast_leave(self, user: User):
        packet = {
            "header": "user-leave",
            "user": user.build_json()
        }

        for client in self.clients:
            DataTransfer.send_packet(client, packet)

    '''
    Announces information to each client
    '''
    def broadcast_announcement(self, announcement: Announcement):
        packet = announcement.build_packet()

        for client in self.clients:
            DataTransfer.send_packet(client, packet)

    '''
    Sends every connected user to a client
    - Useful is a client is not the first to connect, they will be sent this
    '''
    def send_users(self, client: Client):
        users = []

        for _client in self.clients:
            if _client != client and _client.received_user:
                users.append(_client.user.build_packet())

        packet = {
            "header": "users",
            "array": users
        }

        DataTransfer.send_packet(client, packet)

    '''
    Sends every message to a client
    - Useful if a client connects later on in the chat and needs to be told what the previous messages were
    '''
    def send_messages(self, client: Client):
        messages = []

        for message in self.messages:
            messages.append(message.build_packet())

        packet = {
            "header": "messages",
            "array": messages
        }

        DataTransfer.send_packet(client, packet)

if __name__ == "__main__":
    server = ChatRoomServer(socket.gethostname(), 1024)
    server.start()

