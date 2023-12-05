# encoding:utf-8

import time
import struct
import socket
import select
import sys
from typing import DefaultDict


class PING:
    IP_HEADER_LENGTH = 20
    # ICMP报文类型 => 回送请求报文
    TYPE_ECHO_REQUEST = 8
    CODE_ECHO_REQUEST_DEFAULT = 0

    def chesksum(self, data):
        n = len(data)
        m = n % 2
        sum = 0
        for i in range(0, n - m, 2):
            sum += (data[i]) + (
                (data[i + 1]) << 8
            )  #传入data以每两个字节（十六进制）通过ord转十进制，第一字节在低位，第二个字节在高位
        if m:
            sum += (data[-1])
        #将高于16位与低16位相加
        sum = (sum >> 16) + (sum & 0xffff)
        sum += (sum >> 16)  #如果还有高于16位，将继续与低16位相加
        answer = ~sum & 0xffff
        #  主机字节序转网络字节序列（参考小端序转大端序）
        answer = answer >> 8 | (answer << 8 & 0xff00)
        return answer

    def request_ping(self, data_type, data_code, data_checksum, data_ID,
                     data_Sequence, payload_body):
        #  把字节打包成二进制数据
        imcp_packet = struct.pack('>BBHHH32s', data_type, data_code,
                                  data_checksum, data_ID, data_Sequence,
                                  payload_body)
        icmp_chesksum = self.chesksum(imcp_packet)  #获取校验和
        #  把校验和传入，再次打包
        imcp_packet = struct.pack('>BBHHH32s', data_type, data_code,
                                  icmp_chesksum, data_ID, data_Sequence,
                                  payload_body)
        return imcp_packet

    def raw_socket(self, dst_addr, imcp_packet):
        '''
        连接套接字,并将数据发送到套接字
        '''

        #实例化一个socket对象，ipv4，原套接字，分配协议端口
        rawsocket = socket.socket(socket.AF_INET, socket.SOCK_RAW,
                                  socket.getprotobyname("icmp"))

        #记录当前请求时间
        send_request_ping_time = time.time()
        #发送数据到网络
        rawsocket.sendto(imcp_packet, (dst_addr, 80))
        #返回数据
        return send_request_ping_time, rawsocket, dst_addr

    def reply_ping(self,
                   send_request_ping_time,
                   rawsocket,
                   data_Sequence,
                   timeout=5):
        while True:
            #开始时间
            started_select = time.time()
            #实例化select对象，可读rawsocket，可写为空，可执行为空，超时时间
            what_ready = select.select([rawsocket], [], [], timeout)
            #等待时间
            wait_for_time = (time.time() - started_select)
            #没有返回可读的内容，判断超时
            if what_ready[0] == []:  # Timeout
                return -1
            #记录接收时间
            time_received = time.time()
            #设置接收的包的字节为1024
            received_packet, addr = rawsocket.recvfrom(1024)
            #获取接收包的icmp头
            icmpHeader = received_packet[20:28]
            #反转编码
            type, code, checksum, packet_id, sequence = struct.unpack(
                ">BBHHH", icmpHeader)

            ttl = self.parse_ip_header(received_packet[:20])

            if type == 0 and sequence == data_Sequence:
                return time_received - send_request_ping_time, ttl

            #数据包的超时时间判断
            timeout = timeout - wait_for_time
            if timeout <= 0:
                return -1, ttl

    def parse_ip_header(self, ip_header):
        """
        IP报文格式
        1. 4位IP-version 4位IP头长度 8位服务类型 16位报文总长度
        2. 16位标识符 3位标记位 13位片偏移 暂时不关注此行
        3. 8位TTL 8位协议 16位头部校验和
        4. 32位源IP地址
        5. 32位目的IP地址
        :param ip_header:
        :return:
        """
        line1 = struct.unpack('>BBH', ip_header[:4])  # 先按照8位、8位、16位解析
        ip_version = line1[0] >> 4  # 通过右移4位获取高四位
        # 报文头部长度的单位是32位 即四个字节
        iph_length = (line1[0] & 15) * 4  # 与1111与运算获取低四位
        packet_length = line1[2]
        line3 = struct.unpack('>BBH', ip_header[8:12])
        TTL = line3[0]
        protocol = line3[1]
        iph_checksum = line3[2]
        line4 = struct.unpack('>4s', ip_header[12:16])
        src_ip = socket.inet_ntoa(line4[0])
        line5 = struct.unpack('>4s', ip_header[16:20])
        dst_ip = socket.inet_ntoa(line5[0])

        return {
            'ip_version': ip_version,
            'iph_length': iph_length,
            'packet_length': packet_length,
            'TTL': TTL,
            'protocol': protocol,
            'iph_checksum': iph_checksum,
            'src_ip': src_ip,
            'dst_ip': dst_ip
        }

    def ping(self, host):
        send, accept, lost = 0, 0, 0
        sumtime, shorttime, longtime, avgtime = 0, 1000, 0, 0
        #icmp数据包的构建
        data_checksum = 0  # "...with value 0 substituted for this field..."
        data_ID = 0  #Identifier
        data_Sequence = 1  #Sequence number
        payload_body = b'abcdefghijklmnopqrstuvwabcdefghi'  #data

        # 将主机名转ipv4地址格式，返回以ipv4地址格式的字符串，如果主机名称是ipv4地址，则它将保持不变
        dst_addr = socket.gethostbyname(host)

        print("\n正在 Ping {0} [{1}] 具有 32 字节的数据:".format(host, dst_addr))
        for i in range(0, 4):
            send = i + 1
            #请求ping数据包的二进制转换
            icmp_packet = self.request_ping(self.TYPE_ECHO_REQUEST,
                                            self.CODE_ECHO_REQUEST_DEFAULT,
                                            data_checksum, data_ID,
                                            data_Sequence + i, payload_body)
            #连接套接字,并将数据发送到套接字
            send_request_ping_time, rawsocket, addr = self.raw_socket(
                dst_addr, icmp_packet)
            #数据包传输时间
            times, ttl = self.reply_ping(send_request_ping_time, rawsocket,
                                         data_Sequence + i)

            if times > 0:
                print("来自 {0} 的回复: 字节 = 32 时间 = {1}ms TTL = {2} ".format(
                    addr, int(times * 1000), ttl['TTL']))
                accept += 1
                return_time = int(times * 1000)
                sumtime += return_time
                longtime = max(longtime, return_time)
                shorttime = min(return_time, shorttime)
                time.sleep(0.7)
            else:
                lost += 1
                print("请求超时。")

            if send == 4:
                print("\n{0} 的 Ping 统计信息:".format(dst_addr))
                print(
                    "\t数据包：已发送 = {0},接收 = {1}，丢失 = {2}（{3}%丢失），\n往返行程的估计时间（以毫秒为单位）：\n\t最短 = {4}ms，最长 = {5}ms，平均 = {6}ms"
                    .format(i + 1, accept, lost, lost / (i + 1) * 100,
                            shorttime, longtime, sumtime / send))


class TraceRoute(PING):
    # ICMP报文类型 => 回送请求报文
    TYPE_ECHO_REQUEST = 8
    CODE_ECHO_REQUEST_DEFAULT = 0
    # ICMP报文类型 => 回送应答报文
    TYPE_ECHO_REPLY = 0
    CODE_ECHO_REPLY_DEFAULT = 0

    # ICMP报文类型 => 数据报超时报文
    TYPE_ICMP_OVERTIME = 11
    CODE_TTL_OVERTIME = 0

    # ICMP报文类型 => 目的站不可达报文
    TYPE_ICMP_UNREACHED = 3
    CODE_NET_UNREACHED = 0
    CODE_HOST_UNREACHED = 1
    CODE_PORT_UNREACHED = 3

    MAX_HOPS = 30  # 设置路由转发最大跳数为30
    TIMEOUT = 5 # 如果一个请求超过1s未得到响应，则被认定为超时
    TRIES = 3  # 对于每个中间站点，探测的次数设置为3

    def traceroute_raw_socket(self, dst_addr, imcp_packet, ttl):
        #实例化一个socket对象，ipv4，原套接字，分配协议端口
        rawsocket = socket.socket(socket.AF_INET, socket.SOCK_RAW,
                                  socket.getprotobyname("icmp"))
        rawsocket.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)
        #记录当前请求时间
        send_request_traceroute_time = time.time()
        #发送数据到网络
        rawsocket.sendto(imcp_packet, (dst_addr, 80))
        #返回数据
        return send_request_traceroute_time, rawsocket, dst_addr

    def build_imcp_packet(self, host):
        #icmp数据包的构建
        data_checksum = 0  # "...with value 0 substituted for this field..."
        data_ID = 0  #Identifier
        data_Sequence = 1  #Sequence number
        payload_body = b'abcdefghijklmnopqrstuvwabcdefghi'  #data

        #  把字节打包成二进制数据
        imcp_packet = struct.pack('>BBHHH32s', self.TYPE_ECHO_REQUEST,
                                  self.CODE_ECHO_REQUEST_DEFAULT,
                                  data_checksum, data_ID, data_Sequence,
                                  payload_body)
        icmp_chesksum = self.chesksum(imcp_packet)  #获取校验和
        #  把校验和传入，再次打包
        imcp_packet = struct.pack('>BBHHH32s', self.TYPE_ECHO_REQUEST,
                                  self.CODE_ECHO_REQUEST_DEFAULT,
                                  icmp_chesksum, data_ID, data_Sequence,
                                  payload_body)
        return imcp_packet

    def traceroute(self, host):
        # 将主机名转ipv4地址格式，返回以ipv4地址格式的字符串，如果主机名称是ipv4地址，则它将保持不变
        dst_addr = socket.gethostbyname(host)
        print("\nrouting {0}[{1}](max hops = 30, detect tries = 3)\n".format(
            host, dst_addr))

        for ttl in range(1, self.MAX_HOPS):
            time.sleep(0.5)
            print("{0:<3d}".format(ttl), end="")
            flag = False
            for tries in range(0, self.TRIES):
                imcp_packet = self.build_imcp_packet(host)
                send_request_traceroute_time, rawsocket, dst_addr = self.traceroute_raw_socket(
                    dst_addr, imcp_packet, ttl)
                ready = select.select([rawsocket], [], [], self.TIMEOUT)
                end_time = time.time()
                during_time = end_time - send_request_traceroute_time
                global ip_head, receive_packet, addr
                if during_time >= self.TIMEOUT:
                    print("{0:>7}    ".format('*'), end="")
                else:
                    print("{0:7.2f} ms ".format(during_time * 1000), end="")
                    flag = True
                    receive_packet, addr = rawsocket.recvfrom(1024)
                    ip_head = self.parse_ip_header(receive_packet[:20])

                if (tries >= self.TRIES - 1):
                    if (flag == False):
                        print(" request timeout")
                        break
                    icmp_head = receive_packet[20:28]
                    type, code, checksum, packet_id, sequence = struct.unpack(
                        ">BBHHH", icmp_head)
                    if (type == self.TYPE_ICMP_UNREACHED and flag == False):
                        print(" Wrong!unreached net/host/port!")
                        break
                    elif (type == self.TYPE_ICMP_OVERTIME):
                        print(" {}".format(ip_head['src_ip']))
                    elif (type == 0):
                        print(" {}".format(ip_head['src_ip']))
                        print("program run over!")
                        return
                    else:
                        print(" {}".format(ip_head['src_ip']))


def usage():
    print("Usage: tool.py [-T host ] [-h help] [-P host]\n")
    print("Options:")
    print("       -P       ping <host>")
    print("       -T       traceroute <host>")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        usage()
        sys.exit()
    if (sys.argv[1] == "-P" or sys.argv[1] == "-p"):
        T = PING()
        T.ping(sys.argv[2])
    elif (sys.argv[1] == "-T" or sys.argv[1] == "-t"):
        T = TraceRoute()
        T.traceroute(sys.argv[2])
    else:
        usage()