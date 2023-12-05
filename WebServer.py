
def handleRequest(tcpSocket):
    try:
        # 1. Receive request message from the client on connection socket
        requestMessage = tcpSocket.recv(1024).decode('utf-8')

        # 2. Extract the path of the requested object from the message (second part of the HTTP header)
        requestHeaders = requestMessage.split('\r\n')
        if len(requestHeaders) > 0:
            requestLine = requestHeaders[0].split()
            if len(requestLine) > 1:
                path = requestLine[1]
                filePath = path.lstrip("/")

                # 3. Read the corresponding file from disk
                with open(filePath, 'rb') as file:
                    content = file.read()

                # 4. Send the correct HTTP response header and content
                responseHeader = "HTTP/1.1 200 OK\r\n\r\n"
                tcpSocket.sendall(responseHeader.encode('utf-8'))
                tcpSocket.sendall(content)
            else:
                # If the request line is not as expected, send a 400 Bad Request response
                response = "HTTP/1.1 400 Bad Request\r\n\r\n"
                tcpSocket.sendall(response.encode('utf-8'))
    except Exception as e:
        print("Error handling request:", e)
    finally:
        # 7. Close the connection socket
        tcpSocket.close()

def startServer(serverAddress, serverPort):
    # 1. Create server socket
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        # 2. Bind the server socket to server address and server port
        serverSocket.bind((serverAddress, serverPort))

        # 3. Continuously listen for connections to server socket
        serverSocket.listen()

        while True:
            print("Waiting for connections...")
            # 4. When a connection is accepted, call handleRequest function, passing new connection socket
            connectionSocket, clientAddress = serverSocket.accept()
            print("Accepted connection from", clientAddress)
            handleRequest(connectionSocket)
    except Exception as e:
        print("Error starting server:", e)
    finally:
        # 5. Close server socket
        serverSocket.close()

# Call the startServer function with the desired server address and port
startServer("", 8000)
