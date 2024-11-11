#!/usr/bin/python3
import socket
import sys
import csv
from typing import Optional
import select


def read_script_inputs() -> tuple[str, int]:
    port = int(sys.argv[2]) if len(sys.argv) == 3 else 1337
    users_file_path = sys.argv[1]
    return users_file_path, port

def read_users_file(users_file: str) -> list[list[str]]:
    try:
        with open(users_file, 'r') as file:
            return list(csv.reader(file, delimiter='\t'))
    except FileNotFoundError:
        sys.stderr.write("Invalid name of users file\n")
        exit(1)

def parse_user_passwords(rows: list[list[str]]) -> dict[str, str]:
    user_pass_map = {}
    for row in rows:
        if len(row) != 2:
            sys.stderr.write("Invalid users file\n")
            exit(1)
        user, password = row
        user_pass_map[user] = password
    return user_pass_map

class Server:
    def __init__(self):
        self.listening_socket: Optional[socket.socket] = None
        self.port: Optional[int] = None
        self.readable = []
        self.writable = []
        self.exceptions = []
        self.max_clients = 20
        self.users_password_map = {}
        self.setup_server()

    def setup_server(self) -> None:
        self.setup_parameters()
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('', self.port))
        server_socket.listen(self.max_clients)
        print(f"Server listening on port {self.port}, can accept {self.max_clients} clients ")
        self.listening_socket = server_socket
        self.readable.append(self.listening_socket)

    def setup_parameters(self):
        users_file, port = read_script_inputs()
        self.port = port
        file_rows = read_users_file(users_file)
        self.users_password_map = parse_user_passwords(file_rows)
    #Divide this into functions, implement better select logic
    def run(self):
        while True:
            readable, writable, exceptional = select.select(self.readable,
                                                            self.writable,
                                                            self.exceptions,
                                                            0.2)
            for sock in readable:
                if sock == self.listening_socket:
                    client_socket, client_address = self.listening_socket.accept()
                    self.readable.append(client_socket)
                else:
                    try:
                        data = sock.recv(1024)
                        if data:
                            sock.sendall(f"Received: {data.decode()}".encode())
                        else:
                            pass
                            # print(f"Closing connection to {sock.getpeername()}")
                            # sockets_list.remove(sock)
                            # sock.close()
                    except Exception as e:
                        pass
                        # print(f"Error handling client {sock.getpeername()}: {e}")
                        # sockets_list.remove(sock)
                        # sock.close()


def main():
    server = Server()



if __name__ == "__main__":
    main()