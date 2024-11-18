#!/usr/bin/python3
import socket
import sys
import select

def receive_input() -> tuple[str, int]:
    if len(sys.argv) == 1:
        hostname = "localhost"
        port = 1337
    elif len(sys.argv) == 2:
        hostname = sys.argv[1]
        port = 1337
    else:
        hostname = sys.argv[1]
        port = int(sys.argv[2])
    return hostname, port

def build_socket_and_connect(hostname: str, port: int) -> socket.socket:
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((hostname, port))
    return client_socket

def login(client_socket: socket.socket) -> bool:
    user_str = input()
    password_str = input()
    msg = f"{user_str}\n{password_str}"
    client_socket.sendall(msg.encode())
    while True:
        ready_to_read, _, _ = select.select([client_socket], [], [], 2)
        if ready_to_read:
            response = client_socket.recv(1024).decode()
            print(response)
            return "good to see you" in response

def receive_welcome_message(client_socket: socket.socket) -> None:
    while True:
        ready_to_read, _, _ = select.select([client_socket], [], [], 2)
        if ready_to_read:
            print(client_socket.recv(1024).decode())
            return


def try_to_login(client_socket: socket.socket) -> None:
    while not login(client_socket):
        continue

def send_command_and_get_response(client_socket:socket.socket) -> None:
    while True:
        command = input()
        client_socket.sendall(command.encode())
        if command == 'quit':
            return
        while True:
            ready_to_read, _, _ = select.select([client_socket], [], [], 2)
            if ready_to_read:
                response = client_socket.recv(1024).decode()
                print(response)
                break


def main() -> None:
    hostname, port = receive_input()
    client_socket = build_socket_and_connect(hostname, port)
    receive_welcome_message(client_socket)
    try_to_login(client_socket)
    send_command_and_get_response(client_socket)
    client_socket.close()

if __name__ == "__main__":
    main()


