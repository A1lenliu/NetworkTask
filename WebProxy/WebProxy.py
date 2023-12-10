from socket import *
from urllib.parse import urlsplit, quote

def startProxy():
    # Create a proxyServer socket and listen
    ProxyPort = 8899
    ProxySock = socket(AF_INET, SOCK_STREAM)

    # Prepare a server socket
    ProxySock.bind(('', ProxyPort))
    ProxySock.listen(5)

    while True:
        # Start accepting connections from clients
        print('Ready to serve...')
        ClientSock, Client_addr = ProxySock.accept()
        print('Received a connection from: ', Client_addr)

        # Receive the request from the client
        request_lines = ClientSock.recv(4096).decode('utf-8')

        # Parse the filename from the request
        url_parts = urlsplit(request_lines.split()[1])
        hostname = url_parts.netloc
        filename = quote(url_parts.path)
        fileExist = "false"
        cache = "./" + hostname + "_" + filename.replace("/", "_")

        try:
            # Check if the file exists in the cache and if it's still valid
            with open(cache, "rb") as f:
                cached_file = f.read()
                fileExist = "true"
                print('File Exists in cache!')

            # If the file exists in the cache, send it to the client
            ClientSock.send("HTTP/1.1 200 OK\r\n\r\n".encode('utf-8'))
            ClientSock.sendall(cached_file)
            print('Read from cache')

        except IOError:
            print('File Exist: ', fileExist)
            if fileExist == "false":
                # Create a TCP socket on the proxy server
                print('Creating socket on proxyServer')
                originSerSocket = socket(AF_INET, SOCK_STREAM)

                print('Host Name: ', hostname)
                try:
                    # Connect to the remote server on port 80
                    originSerSocket.connect((hostname, 80))
                    print('Socket connected to port 80 of the host')

                    # Cache the requested file on the proxy server

                    with open(cache, "wb") as tmpFile:
                        # Construct the HTTP GET request line
                        request_line = "GET " + filename + " HTTP/1.1\r\nHost: " + hostname + "\r\n\r\n"
                        originSerSocket.send(request_line.encode('utf-8'))

                        # Read the response into buffer
                        print('Sent request to remote server:', request_line)
                        buff = originSerSocket.recv(4096)
                        print('Received response from remote server:', buff)
                        tmpFile.write(buff)

                        # Send the response to the client socket and cache the file
                        ClientSock.send("HTTP/1.1 200 OK\r\n\r\n".encode('utf-8'))
                        ClientSock.sendall(buff)

                except Exception as e:
                    print("Exception: ", e)
                    # Send a custom 404 Not Found page in case of an error
                    error_page = "HTTP/1.1 404 Not Found\r\n\r\n<html><body><h1>Custom 404 Not Found Page</h1></body></html>"
                    ClientSock.send(error_page.encode('utf-8'))

        # Close the client and server sockets
        ClientSock.close()

    # Close the proxy server socket
    ProxySock.close()

# Start the proxy server
startProxy()
