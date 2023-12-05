import socket
from urllib.parse import unquote

def handle_request(client_socket):
    content = b''  # Initialize content variable outside the try block
    try:
        # ... (keep the original request handling code)

        # 准备200 OK响应头
        response_header = "HTTP/1.1 200 OK\r\n"
        server_info = "Server: SimpleHTTPServer\r\n"
        # 组装完整的HTTP响应
        response = response_header + server_info + "\r\n" + content.decode("utf-8")
        client_socket.sendall(response.encode("utf-8"))  # 向客户端发送响应

    except FileNotFoundError:
        # 准备404 Not Found响应头
        response_header = "HTTP/1.1 404 Not Found\r\n"
        server_info = "Server: SimpleHTTPServer\r\n"
        # 组装完整的HTTP错误响应
        response = response_header + server_info + "\r\n" + "File Not Found\nCheck your input\n"
        client_socket.sendall(response.encode("utf-8"))  # 向客户端发送错误响应

    finally:
        client_socket.close()  # 关闭客户端套接字

def start_server(server_addr, server_port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 创建TCP套接字
    server_socket.bind((server_addr, server_port))  # 绑定地址和端口
    server_socket.listen(0)  # 开始监听
    try:
        while True:
            print("waiting for connecting...")
            client_socket, client_addr = server_socket.accept()  # 接受一个新连接
            print("one connection is established and its address is: %s" % str(client_addr))
            handle_request(client_socket)  # 调用后端函数处理请求
            print("client close")
    except Exception as err:
        print(err)
    finally:
        server_socket.close()  # 关闭服务器套接字

# 启动服务器
start_server("127.0.0.1", 8080)
