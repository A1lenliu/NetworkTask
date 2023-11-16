#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import socket
import os
import sys
import struct
import time
import select
import binascii

ICMP_ECHO_REQUEST = 8  # ICMP type code for echo request messages
ICMP_ECHO_REPLY = 0  # ICMP type code for echo reply messages


def checksum(data):
    # Calculate the ICMP checksum
    # This function is unchanged from your original code
    csum = 0
    countTo = (len(data) // 2) * 2
    count = 0

    while count < countTo:
        thisVal = data[count + 1] * 256 + data[count]
        csum = csum + thisVal
        csum = csum & 0xffffffff
        count = count + 2

    if countTo < len(data):
        csum = csum + data[len(data) - 1]
        csum = csum & 0xffffffff

    csum = (csum >> 16) + (csum & 0xffff)
    csum = csum + (csum >> 16)
    answer = ~csum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)

    answer = socket.htons(answer)

    return answer


def receiveOnePing(icmpSocket, destinationAddress, ID, timeout):
    timeLeft = timeout

    while True:
        startedSelect = time.time()
        whatReady = select.select([icmpSocket], [], [], timeLeft)
        howLongInSelect = (time.time() - startedSelect)

        if whatReady[0] == []:  # Timeout
            return -1

        timeReceived = time.time()
        recPacket, addr = icmpSocket.recvfrom(1024)

        # Extract the ICMP header from the received packet
        icmpHeader = recPacket[20:28]

        # Unpack the received header
        type, code, checksum, packetID, sequence = struct.unpack("bbHHh", icmpHeader)

        if packetID == ID:
            bytesInDouble = struct.calcsize("d")
            timeSent = struct.unpack("d", recPacket[28:28 + bytesInDouble])[0]
            return timeReceived - timeSent

        timeLeft = timeLeft - howLongInSelect
        if timeLeft <= 0:
            return -1


def sendOnePing(icmpSocket, destinationAddress, ID):
    # Header is type (8), code (8), checksum (16), id (16), sequence (16)
    myChecksum = 0

    # Make a dummy header with a 0 checksum
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, myChecksum, ID, 1)
    bytesInDouble = struct.calcsize("d")
    data = (192 - bytesInDouble) * "Q"
    data = struct.pack("d", time.time()) + bytes(data.encode('utf-8'))

    # Calculate the checksum on the data and the dummy header.
    myChecksum = checksum(header + data)

    # Now that we have the right checksum, we put that in. It's just easier to make up a new header than to stuff it into the dummy.
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, socket.htons(myChecksum), ID, 1)
    packet = header + data
    icmpSocket.sendto(packet, (destinationAddress, 1))


def doOnePing(destinationAddress, timeout):
    icmp = socket.getprotobyname("icmp")
    try:
        icmpSocket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
    except socket.error as e:
        if e.errno == 1:
            # Operation not permitted, running as non-root
            raise PermissionError("ICMP messages can only be sent from a process running as root")
        else:
            raise

    myID = os.getpid() & 0xFFFF  # Identify the process

    sendOnePing(icmpSocket, destinationAddress, myID)
    delay = receiveOnePing(icmpSocket, destinationAddress, myID, timeout)

    icmpSocket.close()
    return delay


def ping(host, timeout=1):
    dest = socket.gethostbyname(host)
    print(f"Pinging {host} [{dest}] with timeout {timeout} seconds:")

    try:
        while True:
            delay = doOnePing(dest, timeout)
            if delay == -1:
                print("Request timed out.")
            else:
                print(f"Round Trip Time: {delay * 1000:.6f} ms")
            time.sleep(1)  # Ping approximately every second

    except KeyboardInterrupt:
        print("\nPing stopped by the user.")


# Usage example
ping("lancaster.ac.uk")
