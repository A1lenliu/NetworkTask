import socket
import struct
import time

def traceroute(target, max_hops=30, timeout=1):
    for ttl in range(1, max_hops + 1):
        # 创建UDP套接字
        udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        udp_socket.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)

        # 设置超时时间
        udp_socket.settimeout(timeout)

        try:
            # 发送UDP数据包
            udp_socket.sendto(b"", (target, 33434))

            # 接收响应
            start_time = time.time()
            _, addr = udp_socket.recvfrom(512)
            end_time = time.time()

            # 获取路由器的IP地址
            ip = struct.unpack("!BBHHHBBH4s4s", _[:20])[8]
            ip_address = socket.inet_ntoa(ip)

            # 打印跃点信息
            print(f"{ttl}: {ip_address}  {round((end_time - start_time) * 1000)} ms")

            # 如果已到达目标主机，跳出循环
            if ip_address == target:
                break

        except socket.timeout:
            print(f"{ttl}: *")
        finally:
            udp_socket.close()

if __name__ == "__main__":
    target_host = "lancaster.ac.uk"
    traceroute(target_host)
