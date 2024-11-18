# Client-Server Protocol Overview

## Introduction
This system implements a client-server architecture where the client logs in to the server and sends various commands,
such as calculation requests and queries, which the server processes and responds to.
The server requires user authentication before executing commands.

---

## Server Instructions

### Usage
Run the server script:
python3 server.py <users_file> [port]

- <users_file>: Tab-delimited file containing valid usernames and passwords.
  - Example format:
    user1    pass1
    user2    pass2
- [port]: Optional port number. Default is 1337.

### Workflow
1. The server listens for client connections.
2. Upon connection, the server sends:
   Welcome! Please log in.
3. Once the client logs in successfully, the server processes commands and responds accordingly.

---

## Error Handling
- If a command is malformed or unsupported, the server responds with:
  Invalid command format
  or
  Invalid command
  alongside the correct format as an example
- If the result of a calculation overflows a 32-bit integer, the server responds with:
  error: result is too big


## Client Instructions

### Usage
Run the client script:
python3 numbers_client.py [hostname] [port]

- If no hostname or port is provided, defaults are:
  - hostname: localhost
  - port: 1337

### Workflow
- At any point even before logging in you can use the 'quit' command. Refer to commands for information.
1. **Login**:
   - The client sends a username and password to the server.
   - Format:
     User: <username>
     Password: <password>
   - If login is successful, the server responds with:
     Hi <username>, good to see you.
   - If login fails, the server responds with:
     Failed to login.
     And you again are required to attempt to login.


2. **Commands**:
   - After successful login, the client can send the following commands:

     a. **Max Command**
        Finds the maximum number from a list.
        - Format:
          max: (num1 num2 num3 ...)
        - Response:
          the maximum is <result>

     b. **Factors Command**
        Finds the prime factors of a number, sorted in ascending order.
        Factors can be duplicated. e.g. the factors of 4 are 2, 2
        - Format:
          factors: <number>
        - Response:
          The prime factors of <number> are: <factor1>, <factor2>, ...


     c. **Calculate Command**
        Performs arithmetic operations.
        - Format:
          calculate: <num1> <operator> <num2>
        - Supported operators:
          + (addition)
          - (subtraction)
          * (multiplication)
          / (division, rounded to 2 decimals)
          ^ (exponentiation)
        - Response:
          response: <result>.

     d. **Quit**
        Terminates the connection.
        - Format:
          quit

---
