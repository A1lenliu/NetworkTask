import socket
from urllib.parse import unquote
import threading


# 修改 handle_request 函数，添加额外的输出
def handle_request(client_socket):
    content = b''  # 初始化 content 变量为空字节串
    try:
        requestData = client_socket.recv(1024)
        requestList = requestData.decode().split("\r\n")
        reqHeaderLine = requestList[0]
        print("Received request: " + reqHeaderLine)  # 输出收到的请求行
        fileName = reqHeaderLine.split(" ")[1].split("/")[-1]

        print("Requested file: " + fileName)  # 输出请求的文件名

        # 判断是否为代理请求，如果是则调用代理函数处理
        if fileName.lower() == "proxy":
            start_proxy(8888, client_socket)
            return

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
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((server_addr, server_port))
    server_socket.listen(0)

    try:
        while True:
            print("Waiting for connection...")
            client_socket, client_addr = server_socket.accept()
            print("One connection is established and its address is: %s" % str(client_addr))
            # 创建线程处理每个连接
            client_thread = threading.Thread(target=handle_request, args=(client_socket,))
            client_thread.start()
    except Exception as err:
        print(err)
    finally:
        server_socket.close()


# 代理服务器的 start_proxy 函数
def start_proxy(port, client_socket):
    proxyServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxyServerSocket.bind(("127.0.0.1", port))
    proxyServerSocket.listen(0)

    while True:
        try:
            target_socket, target_addr = proxyServerSocket.accept()
            print("Proxy connection established with: %s" % str(target_addr))

            # 创建两个线程，分别从客户端到目标服务器和从目标服务器到客户端转发数据
            client_to_target_thread = threading.Thread(target=forward_data, args=(client_socket, target_socket))
            target_to_client_thread = threading.Thread(target=forward_data, args=(target_socket, client_socket))

            # 启动线程
            client_to_target_thread.start()
            target_to_client_thread.start()

            # 等待两个线程结束
            client_to_target_thread.join()
            target_to_client_thread.join()

            # 关闭目标服务器套接字
            target_socket.close()
        except Exception as e:
            print("Proxy error: {0}".format(e))
            break

    # 关闭代理服务器套接字
    proxyServerSocket.close()


def forward_data(src, dest):
    """
    从源套接字读取数据并将其写入目标套接字
    :param src: 源套接字
    :param dest: 目标套接字
    :return: 无
    """
    while True:
        data = src.recv(4096)
        if not data:
            break
        dest.sendall(data)


# 启动服务器
start_server("127.0.0.1", 8080)
