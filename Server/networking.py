
from threading import Thread, Lock
import socket
import json
import time

'''
Client class
- Stores useful information about a client, such as the ip and socket
'''
class Client:
    def __init__(self, ip: str, port: int, sock: socket.socket):
        self.ip = ip
        self.port = port
        self.sock = sock
        self.received_user = False
        self.user = None
        self.sendlock = Lock()

'''
Static class used for transferring data over a network
'''
class DataTransfer:
    '''
    Sends a dictionary packet to a client
    - Serialises and encodes the packet and then sends it
    '''
    @classmethod
    def send_packet(cls, client: Client, packet: dict):
        serial = json.dumps(packet)
        cls.send_data(client, serial.encode())

    '''
    Opens a thread to send raw data to a client
    '''
    @classmethod
    def send_data(cls, client: Client, data: bytes):
        Thread(target = cls._send_data, args = (client, data)).start()

    '''
    Receives a dictionary packet from a client
    - Decodes and deserialises data received
    '''
    @classmethod
    def recv_packet(cls, client: Client, bufferlen: int):
        data = cls.recv_data(client, bufferlen)
        return json.loads(data.decode())

    '''
    Receives a certain amount of bytes from a client
    '''
    @classmethod
    def recv_data(cls, client: Client, bufferlen: int):
        return client.sock.recv(bufferlen)

    '''
    Sends data to a client in a thread safe manner
    - Ensures data sending is synced between all the threads calling it
    - Allows the receiver to receive data one packet at a time to prevent overlapping packets
    - Only locks each client's socket, there is no universal lock for the clients
    - Allows for a max of 10 packets per second to be sent to a client
    '''
    @classmethod
    def _send_data(cls, client: Client, data: bytes):
        client.sendlock.acquire()
        time.sleep(0.1)
        client.sock.send(data)
        client.sendlock.release()

    '''
    Checks to see if a socket is connected or not
    - Tries to send a dummy packet to the socket, if it failed it is not connected
    '''
    @classmethod
    def socket_is_connected(cls, sock: socket.socket):
        packet = {
            "header": "connection-test"
        }

        serial = json.dumps(packet)

        try:
            sock.send(serial.encode())
            return True
        except:
            return False

