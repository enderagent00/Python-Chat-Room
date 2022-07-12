
from threading import Thread, Lock
import socket
import json
import time

'''
Static class used for transferring data over a network
'''
class DataTransfer:
    lock = Lock()

    '''
    Sends a dictionary packet to a socket
    - Serialises and encodes the packet and then sends it
    '''
    @classmethod
    def send_packet(cls, sock: socket.socket, packet: dict):
        serial = json.dumps(packet)
        cls.send_data(sock, serial.encode())

    '''
    Opens a thread to send raw data to a socket
    '''
    @classmethod
    def send_data(cls, sock: socket.socket, data: bytes):
        Thread(target = cls._send_data, args = (sock, data)).start()

    '''
    Receives a dictionary packet from a socket
    - Decodes and deserialises data received
    '''
    @classmethod
    def recv_packet(cls, sock: socket.socket, bufferlen: int):
        data = cls.recv_data(sock, bufferlen)
        return json.loads(data.decode())

    '''
    Receives a certain amount of bytes from a socket
    '''
    @classmethod
    def recv_data(cls, sock: socket.socket, bufferlen: int):
        return sock.recv(bufferlen)

    '''
    Sends data to a socket in a thread safe manner
    - Ensures data sending is synced between all the threads calling it
    - Allows the receiver to receive data one packet at a time to prevent overlapping packets
    - Allows for a max of 10 packets per second to be sent to the server
    '''
    @classmethod
    def _send_data(cls, sock: socket.socket, data: bytes):
        cls.lock.acquire()
        time.sleep(0.1)
        sock.send(data)
        cls.lock.release()

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

