# NetworkTask

1.recreate the **ping** client

By measuring the amount of time taken to receive that response, we can determine the delay in the network. 

Additional features are 1. Accept IP or host name as parameter 2. Display minimum, average, and maximum latency after stopping

2. recreate the traceroute tool

3. WebServe



1. What is the primary purpose of the ICMP Ping tool?
   - ICMP（Internet Control Message Protocol）Ping的主要用途是测试互联网协议（IP）网络上主机的可达性。它发送一个请求到目标主机，如果主机可达，它会回复一个确认。Ping还用于测量数据包从源到目的地再返回的往返时间。
2. **How do you calculate the network delay using the Ping tool?**
   - 网络延迟，通常称为“ping时间”或“往返时间”，是通过测量ICMP Echo Request数据包从源到目的地再返回所花费的时间来计算的。延迟通常以毫秒（ms）为单位报告，这是网络响应和延迟的指标。
3. **What is the main difference in the implementation of Traceroute compared to the ICMP Ping tool?：**
   - 虽然ICMP Ping测试主机的可达性并测量到达目标的往返时间，但Traceroute更进一步。Traceroute跟踪数据包到达目的地的路径，显示沿途的每一跳和数据包到达每一跳所需的时间。Traceroute提供了对网络路径的更详细视图，并有助于识别网络问题。
4. What are some challenges you might face when testing your ICMP Ping application?
   - 在测试ICMP Ping应用程序时可能面临的一些挑战包括处理防火墙或阻止ICMP流量的安全措施，处理不同的网络条件，并确保在不同的情景下进行准确的时间测量。此外，应用程序应在各种情况下优雅地处理错误。
5. **What is the primary function of an HTTP Web Server?**
   - HTTP Web服务器的主要功能是处理来自客户端（例如Web浏览器）的HTTP请求，并用所请求的网页或资源进行响应。它是托管和传递Web内容的基础，促进客户端和Web应用程序之间的通信。
6. **What are some challenges you might encounter when testing the Web Proxy?**
   - 测试Web代理涉及一些挑战，如确保正确处理各种HTTP方法，正确处理缓存机制，验证安全（HTTPS）连接，测试在重负载下的可伸缩性和性能，以及确保它在处理不同类型的内容和Web应用程序时表现正常。安全性测试也至关重要，以识别潜在的漏洞。

1. **Q: 为什么使用 ICMP Ping 工具**
   - **A:** ICMP Ping 工具主要用于测试目标主机的可达性和测量网络往返时间。
2. **Q: 在 Ping 工具中，如何计算网络延迟？**
   - **A:** 网络延迟是通过测量 ICMP Echo Request 数据包从源到目的地再返回所花费的时间来计算的。
3. **Q: Traceroute 和 ICMP Ping 工具的主要实现差异是什么？**
   - **A:** Traceroute 用于跟踪数据包的路径，显示每个跳跃的时间。与 ICMP Ping 不同，Traceroute 提供了关于数据包路径的更详细的信息。
4. **Q: 测试 ICMP Ping 应用程序时可能面临的挑战是什么？**
   - **A:** 挑战可能包括处理防火墙、不同网络条件和确保准确的时间测量。
5. **Q: HTTP Web 服务器的主要功能是什么？**
   - **A:** HTTP Web 服务器的主要功能是处理来自客户端的 HTTP 请求并响应请求的网页或资源。
6. **Q: 测试 Web 代理时可能遇到的挑战有哪些？**
   - **A:** 挑战可能包括确保代理正确处理各种 HTTP 方法、缓存、HTTPS 连接，以及测试在不同负载下的性能和安全性。
   
     
   
     在TASK1.1中我实现了通过构建和解析ICMP报文，使用套接字发送和接收数据和解析IP头部信息，实现了PING功能，我通过循环发送ICMP请求，等待响应后，统计相关信息。
   
     在PING中我使用了
   
     chesksum方法：
   
     该方法用于计算ICMP报文的校验和。
     通过对每两个字节进行加和，处理奇数长度的情况，最终得到16位校验和。
     实现了主机字节序到网络字节序的转换。
     request_ping方法：
   
     该方法用于构建ICMP请求报文。
     使用struct.pack方法将各个字段打包成二进制数据。
     调用chesksum方法计算校验和，并将其替换到报文中。
     raw_socket方法：
   
     该方法用于连接套接字并将ICMP请求报文发送到套接字。
     使用原始套接字 (socket.SOCK_RAW) 来发送 ICMP 报文。
     返回发送请求的时间、套接字对象和目标地址。
     reply_ping方法：
   
     该方法用于处理ICMP响应。
     使用select函数等待套接字可读，并处理超时情况。
     解析接收到的 ICMP 响应头部，并判断是否为预期的响应。
     parse_ip_header方法：
   
     该方法用于解析 IP 头部信息。
     通过struct.unpack方法解析 IP 头部的各个字段，包括版本、头部长度、TTL 等。
     ping方法：
   
     该方法是整个 Ping 过程的入口。
     通过循环发送 ICMP 请求，等待响应，并统计丢包率和往返时间。
     使用raw_socket方法发送 ICMP 请求，通过reply_ping方法处理响应。
   
     在TASK1.2中，由于traceroute方法和ping方法类似，所以我的traceroute类继承了PING类，通过创建套接字，并设置TTL，通过逐步增加TTL，发送ICMP请求，等待响应，记录相关信息。
   
     在TRACEROUTE中我使用了
   
     traceroute_raw_socket方法：
   
     该方法用于创建原始套接字，设置 TTL，并将 ICMP 请求报文发送到套接字。
     返回发送请求的时间、套接字对象和目标地址。
     build_imcp_packet方法：
   
     该方法用于构建 ICMP 请求报文。
     使用struct.pack方法将各个字段打包成二进制数据。
     调用chesksum方法计算校验和，并将其替换到报文中。
     traceroute方法：
   
     该方法是整个 Traceroute 过程的入口。
     使用循环依次增加 TTL，通过traceroute_raw_socket方法发送 ICMP 请求，并等待响应。
     处理 ICMP 响应，包括解析 IP 头部信息，判断是否到达目标，记录相关信息。
     打印每个 TTL 的信息，直到到达目标或超过最大跳数。

