import socket
import sys
import select

if len(sys.argv == 1): #host and port are defualt
    hostname = "local host"
    port = 1337
elif len(sys.argv) == 2: #only port is default
    hostname = sys.argv[1]
    port = 1337
elif len(sys.argv) == 3:
    hostname = sys.argv[1]
    port = int(sys.argv[2])

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((hostname, port))

def login(client_socket):
    # Prompt the user for credentials
    username = input("Enter username: ")
    password = input("Enter password: ")

    # Send credentials to the server in the expected format using sendall
    client_socket.sendall(f"User: {username}\n".encode())
    client_socket.sendall(f"Password: {password}\n".encode())

    # Wait for the server's response using select to avoid blocking
    ready_to_read, _, _ = select.select([client_socket], [], [], 5)  # 5-second timeout
    if ready_to_read:
        response = client_socket.recv(1024).decode()
        print(response)  # Show the server's response

        # Check if login was successful based on the response
        return "good to see you" in response
    else:
        return False

# Receive welcome message using select
ready_to_read, _, _ = select.select([client_socket], [], [], 5)  # 5-second timeout
if ready_to_read:
    print(client_socket.recv(1024).decode())
else:
    print("Failed to receive welcome message. Exiting.")
    client_socket.close()
    sys.exit(1)

# Log in
if not login(client_socket):
    print("Failed to login. Exiting.")
    client_socket.close()
    sys.exit(1)

while True:
    command = input("Enter command: ")
    client_socket.sendall(command.encode())  # Use sendall for reliability

    # Use select to wait for the server's response
    ready_to_read, _, _ = select.select([client_socket], [], [], 5)  # 5-second timeout
    if ready_to_read:
        response = client_socket.recv(1024).decode()
        print(response)
    else:
        print("No response from server. Continuing...")

    if command.strip() == 'quit':
        break

client_socket.close()