import socket
import struct
import time

def traceroute(target, max_hops=30, timeout=2):
    for ttl in range(1, max_hops + 1):
        # 创建 ICMP 套接字
        icmp_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)

        # 设置 IP TTL
        icmp_socket.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)

        # 设置超时时间
        icmp_socket.settimeout(timeout)

        try:
            # 构造 ICMP Echo 请求消息
            icmp_header = struct.pack("BBHHH", 8, 0, 0, 1, 1)
            icmp_checksum = checksum(icmp_header)
            icmp_packet = struct.pack("BBHHH", 8, 0, icmp_checksum, 1, 1)

            # 发送 ICMP Echo 请求消息
            icmp_socket.sendto(icmp_packet, (target, 0))

            # 接收响应
            start_time = time.time()
            _, addr = icmp_socket.recvfrom(512)
            end_time = time.time()

            # 获取路由器的 IP 地址
            ip = struct.unpack("!BBHHHBBH4s4s", _[:20])[8]
            ip_address = socket.inet_ntoa(ip)

            # 打印跃点信息
            print(f"{ttl}: {ip_address}  {round((end_time - start_time) * 1000)} ms")

            # 如果已到达目标主机，跳出循环
            if ip_address == target:
                break

        except socket.timeout:
            print(f"{ttl}: * (Timeout)")
        except socket.error as e:
            print(f"{ttl}: * (Error: {e})")
        finally:
            icmp_socket.close()

def checksum(msg):
    csum = 0
    countTo = (len(msg) // 2) * 2

    count = 0
    while count < countTo:
        thisVal = msg[count+1] * 256 + msg[count]
        csum = csum + thisVal
        csum = csum & 0xffffffff
        count = count + 2

    if countTo < len(msg):
        csum = csum + msg[len(msg) - 1]
        csum = csum & 0xffffffff

    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)

    return answer

if __name__ == "__main__":
    target_host = "lancaster.ac.uk"

    traceroute(target_host)
