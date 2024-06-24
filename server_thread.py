from socket import *
import socket
import threading
import logging
from time import gmtime, strftime
import sys

# Class untuk menangani perintah yang diterima dari klien
class CommandHandler:
    @staticmethod
    def handle_time(connection):
        message = f"JAM {strftime('%H:%M:%S', gmtime())}\r\n"
        connection.sendall(message.encode())

    @staticmethod
    def handle_quit(connection):
        message = "QUIT MESSAGE BERHASIL DITERIMA\n"
        connection.sendall(message.encode())
        connection.close()

    @staticmethod
    def handle_unknown(connection):
        message = "WARNING: COMMAND TIDAK DAPAT DIKENAL\n"
        connection.sendall(message.encode())

# Class yang menangani setiap koneksi klien dalam thread terpisah
class ClientHandler(threading.Thread):
    def __init__(self, connection, address):
        super().__init__()
        self.connection = connection
        self.address = address

    def run(self):
        while True:
            try:
                data = self.connection.recv(32)
                if data:
                    command = data.decode().strip()
                    logging.warning(f"Data diterima: {command} dari klien {self.address}.")
                    if command.endswith('TIME'):
                        logging.warning(f"Menerima perintah TIME dari klien {self.address}.")
                        CommandHandler.handle_time(self.connection)
                    elif command.endswith('QUIT'):
                        logging.warning(f"Menerima perintah QUIT dari klien {self.address}.")
                        CommandHandler.handle_quit(self.connection)
                        break
                    else:
                        logging.warning(f"Perintah tidak dikenal {command} dari klien {self.address}.")
                        CommandHandler.handle_unknown(self.connection)
                else:
                    break
            except OSError:
                break
        self.connection.close()

# Class server yang menunggu koneksi klien dan membuat thread baru untuk masing-masing koneksi
class Server(threading.Thread):
    def __init__(self, host='0.0.0.0', port=45000):
        super().__init__()
        self.host = host
        self.port = port
        self.clients = []
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def run(self):
        self.socket.bind((self.host, self.port))
        self.socket.listen(5)
        logging.warning(f"Server mendengarkan di {self.host}:{self.port}")

        while True:
            connection, client_address = self.socket.accept()
            logging.warning(f"Koneksi dari {client_address}")

            client_thread = ClientHandler(connection, client_address)
            client_thread.start()
            self.clients.append(client_thread)

# Fungsi utama yang memulai server
def main():
    logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
    server = Server()
    server.start()

if __name__ == "__main__":
    main()
