
'''
User Class
- Stores information about a user such as the ID and name
'''
class User:
    def __init__(self, name: str):
        self.name = name
        self.id = -1
    
    def build_json(self):
        return {
            "id": self.id,
            "name": self.name
        }

    def build_packet(self):
        data = self.build_json()
        data["header"] = "user"

        return data
 
    def from_packet(packet: dict):
        user = User(packet["name"])
        user.id = packet["id"]

        return user

'''
Message Class
- Stores information about a message such as the ID, the content of the message and the user that sent it
'''
class Message:
    def __init__(self, content: str, sender: User):
        self.content = content
        self.sender = sender
        self.id = -1

    def build_json(self):
        return {
            "id": self.id,
            "content": self.content,
            "sender": self.sender.build_json()
        }

    def build_packet(self):
        data = self.build_json()
        data["header"] = "message"

        return data

    def from_packet(packet: dict):
        sender = User.from_packet(packet["sender"])
        message = Message(packet["content"], sender)
        message.id = packet["id"]

        return message

'''
Announcement Class
- Stores announcements made by the server, for example when a client connects or disconnects the server will
inform all connected clients of this
'''
class Announcement:
    def __init__(self, content: str):
        self.content = content

    def build_json(self):
        return {
            "content": self.content
        }

    def build_packet(self):
        data = self.build_json()
        data["header"] = "announcement"

        return data

    def from_packet(packet: dict):
        return Announcement(packet["content"])

'''
Constants
- SYSTEM_USER: The user which will be used when making system messages
- SERVER_USER: The user which will be used when making server announcements
- SERVER_DISCONNECTION_MESSAGE: The message text which will be displayed when the server disconnects
'''
SYSTEM_USER = User("System")
SERVER_USER = User("Server")
SERVER_DISCONNECT_MESSAGE = "Server is no longer online. Please try again later"

