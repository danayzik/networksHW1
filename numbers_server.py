#!/usr/bin/python3
import socket
import sys
import csv
from typing import Optional
import select

INT32_MIN = -2147483648
INT32_MAX = 2147483647

def find_factors(n):
    factors = []
    for i in range(1, int(n ** 0.5) + 1):
        if n % i == 0:
            factors.append(i)
            if i != n // i:
                factors.append(n // i)
    return sorted(factors)

def check_int32_overflow(result):
    if result > INT32_MAX or result < INT32_MIN:
        return True
    return False

def add(a: int, b: int) -> int:
    return a + b

def subtract(a: int, b: int) -> int:
    return a - b

def multiply(a: int, b: int) -> int:
    return a * b

def divide(a: int, b: int) -> float:
    return round(float(a) / b, 2)

def power(a: int, b: int) -> int:
    return a ** b

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


class Client:
    def __init__(self, client_socket: socket.socket, address: tuple[str, int]) -> None:
        self.address = address
        self.socket = client_socket
        self.logged_in = False
        self.username: Optional[str] = None
        self.password: Optional[str] = None
        self.message: Optional[bytes] = None


    def login(self, username: str, password: str) -> None:
        self.username = username
        self.password = password
        self.logged_in = True

    def close(self):
        self.socket.close()

class Server:
    def __init__(self):
        self.listening_socket: Optional[socket.socket] = None
        self.port: Optional[int] = None
        self.readable: list[socket.socket] = []
        self.clients: list[Client] = []
        self.max_backlog = 20
        self.users_password_map = {}
        self.valid_commands = ["max", "factors", "calculate"]
        self.setup_server()

    def setup_server(self) -> None:
        self.setup_parameters()
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(('', self.port))
        server_socket.listen(self.max_backlog)
        print(f"Server listening on port {self.port}, can accept {self.max_backlog} clients ")
        self.listening_socket = server_socket

    def setup_parameters(self):
        users_file, port = read_script_inputs()
        self.port = port
        file_rows = read_users_file(users_file)
        self.users_password_map = parse_user_passwords(file_rows)

    # Returns True/False based on success/failure
    def client_login(self, client_connection: Client) -> bool:
        data = client_connection.message
        data_str = data.decode('utf-8')
        lines = data_str.split('\n')
        try:
            line1_header, username = lines[0].split(': ')
            line2_header, password = lines[1].split(': ')
            if line1_header != "User" or line2_header != "Password":
                return False
            if username not in self.users_password_map:
                return False
            if password != self.users_password_map[username]:
                return False
        except Exception as e:
            return False
        client_connection.login(username, password)
        msg = f"Hi {username}, good to see you.\n"
        msg = msg.encode('utf-8')
        self.send_data(client_connection, msg)
        return True

    def send_data(self, client: Client, data: bytes):
        try:
            client.socket.sendall(data)
        except Exception as e:
            self.handle_quit(client)


    def handle_quit(self, client: Client) -> None:
        client.close()
        self.clients.remove(client)

    def handle_new_connections(self):
        if self.listening_socket in self.readable:
            client_socket, client_address = self.listening_socket.accept()
            client = Client(client_socket=client_socket, address=client_address)
            self.clients.append(client)
            self.send_data(client, b"Welcome! Please log in.\n")

    def handle_max_command(self, client: Client, args: str):
        try:
            args = args.strip('()')
            elements = args.split()
            numbers = [int(x) for x in elements]
            max_num = max(numbers)
            self.send_data(client, f"the maximum is {max_num}".encode('utf-8'))
        except Exception as e:
            self.send_data(client, b"Invalid argument")


    def handle_factors_command(self, client: Client, args: str):
        try:
            num = int(args)
        except ValueError:
            self.send_data(client, b"Invalid number")
            return
        primes = find_factors(num)
        msg = f"The prime factors of {num} are: {', '.join(map(str, primes))}"
        self.send_data(client, msg.encode('utf-8'))


    def handle_calculate_command(self, client: Client, args: str):
        valid_operators = ["+", "/", "^", "-", "*"]
        try:
            num1_str, op, num2_str = args.split(" ")
            num1 = int(num1_str)
            num2 = int(num2_str)
        except ValueError:
            self.send_data(client, b"Invalid arguments! Please try again.\n")
            return
        if op not in valid_operators:
            self.send_data(client, b"Invalid operator! Please try again.\n")
            return
        operator_map = {
            "+": add,
            "-": subtract,
            "*": multiply,
            "/": divide,
            "^": power,
        }
        result = operator_map[op](num1, num2)
        if check_int32_overflow(result):
            self.send_data(client, b"error: result is too big")
            return
        self.send_data(client, f"response: {result}.".encode('utf-8'))


    def handle_command(self, client: Client) -> None:
        message = client.message.decode('utf-8')
        if message == "quit":
            self.handle_quit(client)
        try:
            header, args = message.split(": ")
        except ValueError:
            self.send_data(client, b"Invalid command format\nCorrect format:\ncommand: args")
            return
        if header not in self.valid_commands:
            self.send_data(client, b"Invalid command\n")
            return


    #Divide this into functions, implement better select logic
    def run(self):
        while True:
            sockets_lst = [self.listening_socket] + [connection.socket for connection in self.clients]
            self.readable, writable, xlist = select.select(sockets_lst,
                                                            [],
                                                            [],
                                                            0.2)
            self.handle_new_connections()
            #Iterating over all clients and not just readable sockets is inefficient, we know.
            for client in self.clients:
                sock = client.socket
                if sock in self.readable:
                    client.message = sock.recv(1024)
                    if not client.logged_in:
                        if not self.client_login(client):
                            self.send_data(client, b"Failed to login.\n")
                    else:
                        client.message = sock.recv(1024)
                        self.handle_command(client)


def main():
    server = Server()
    server.run()


if __name__ == "__main__":
    main()