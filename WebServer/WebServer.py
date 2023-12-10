import socket
from urllib.parse import unquote
def handle_request(client_socket):
    #这段代码的目标是通过HTTP协议向客户端提供请求的文件内容。如果文件存在，它会返回一个成功的HTTP响应，如果文件不存在，它会返回一个包含“404 Not Found”的错误响应
    content = b''  # 初始化 content 变量为空字节串
    try:
        requestData = client_socket.recv(1024)
        requestList = requestData.decode().split("\r\n")
        reqHeaderLine = requestList[0]
        print("Received request: " + reqHeaderLine)  # 输出收到的请求行
        fileName = reqHeaderLine.split(" ")[1].split("/")[-1]#从请求行中提取请求的文件名

        print("Requested file: " + fileName)  # 输出请求的文件名

        with open("./" + fileName, 'rb') as file:
            content = file.read()

        response_header = "HTTP/1.1 200 OK\r\n"
        server_info = "Server: SimpleHTTPServer\r\n"
        response = response_header + server_info + "\r\n" + content.decode("utf-8")
        client_socket.sendall(response.encode("utf-8"))

    except FileNotFoundError:
        response_header = "HTTP/1.1 404 Not Found\r\n"
        server_info = "Server: SimpleHTTPServer\r\n"
        response = response_header + server_info + "\r\n" + "File Not Found\nCheck your input\n"
        client_socket.sendall(response.encode("utf-8"))

    finally:
        client_socket.close()
        print("Connection closed\n")  # 添加输出语句


# 修改 start_server 函数，添加额外的输出
def start_server(server_addr, server_port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)#ipv4，TCP
    server_socket.bind((server_addr, server_port))#绑定端口和地址
    server_socket.listen(0)

    try:
        while True:
            print("Waiting for connection...")
            client_socket, client_addr = server_socket.accept()
            print("One connection is established and its address is: %s" % str(client_addr))
            handle_request(client_socket)
    except Exception as err:
        print(err)
    finally:
        server_socket.close()


# 启动服务器
start_server("127.0.0.1", 8080)
