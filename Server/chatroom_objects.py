
import random

'''
Object ID Generator
- Generates IDs for objects such as users or messages
- Keeps track of generated IDs so there is no repetition
- Repetition of IDs is extremely unlikely, however this will still account for it
'''
class ObjectIDGenerator:
    ids = []

    @classmethod
    def generate_id(cls):
        id = random.randint(1000000000, 9999999999)

        if id in cls.ids:
            return cls.generate_id()
        else:
            cls.ids.append(id)
            return id

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
        return User(packet["name"])

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
        return Message(packet["content"], sender)

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

