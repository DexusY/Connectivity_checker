import logging
import socket
import binascii
import struct
from datetime import datetime
import threading
 
 
def CRC32_from_file(filename):
    buf = open(filename,'rb').read()
    buf = (binascii.crc32(buf) & 0xFFFFFFFF)
    return buf
 
def string_to_number(text):
    return int(text.encode('utf-8').hex(), 16)

SETI = string_to_number('SETI')
 
class Server_two:
    def __init__(self, local_ip, port, connection_queue, dev_num):
        self.HOST = local_ip
        self.PORT = port
        self.password = b"alamakotagigantaalamakotagiganta"
        self.connection_queue = connection_queue
        self.dev_num = dev_num
        self.connections = {}
        self.lock = threading.Lock()
        self.server_socket = None
 
        self.server_socket = None
        self.connection = None
        self.client_address = None
 
 
    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.HOST, self.PORT))
        self.server_socket.listen(5)
        logging.info(f"[{datetime.now()}] Server Two Listening on {self.HOST}:{self.PORT} ...")
 
        while True:
            connection, client_address = self.server_socket.accept()
            threading.Thread(target=self.handle_client, args=(connection, client_address)).start()
 
    def handle_client(self, connection, client_address):
        data_in = connection.recv(60)
        mac = data_in.decode('utf-8', 'ignore')[3:]
        mac = mac.upper()
        with self.lock:
            self.connections[mac] = connection
        self.connection_queue.put((client_address, mac, 'server_two'))
        logging.info(f"New server connection from {client_address} with MAC {mac}")
 
    def get_connection(self, mac):
        with self.lock:
            return self.connections.get(mac)
 
    def SetErrorTimeout(self, mac, timeout=60):
        connection = self.get_connection(mac)
        if not connection:
            logging.error(f"No connection found for device {mac}")
            return
        try:
            epd_cmd = struct.pack('!cHII', bytes('C', 'utf-8'), 8, SETI, timeout)
            connection.sendall(epd_cmd)
            data_in = connection.recv(60)
            print("SetErrorTimeout...")
            print("received: " + str(struct.unpack("!H", data_in[1:3])[0]) + " bytes")
            print("Timeout: " + str(struct.unpack("!I", data_in[3:7])[0]) + " s")
        except Exception as e:
            logging.error(f"Failed to get device ID from device {mac}: {e}")
 
