import socket
import struct
import time
import select
import os


ICMP_ECHO_REQUEST = 8


def checksum(source_string):
    """
    Calculates the Internet checksum for a given string.
    """

    sum = 0

    count_to = (len(source_string) // 2) * 2

    for count in range(0, count_to, 2):
        this_val = source_string[count + 1] * 256 + source_string[count]
        sum = sum + this_val
        sum = sum & 0xFFFFFFFF  # Ensure 32-bit sum
    if count_to < len(source_string):
        sum = sum + source_string[len(source_string) - 1]
        sum = sum & 0xFFFFFFFF

    sum = (sum >> 16) + (sum & 0xFFFF)
    sum = sum + (sum >> 16)
    answer = ~sum
    answer = answer & 0xFFFF
    answer = answer >> 8 | (answer << 8 & 0xFF00)

    return answer


def do_one_ping(dest_addr, timeout: float = 1.0):
    """
    Sends one ICMP echo request and waits for a reply.
    Returns the delay in seconds or None if timed out.
    """

    try:
        # Create a raw socket with ICMP protocol
        icmp_socket = socket.socket(
            socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP
        )

    except socket.error as e:
        if e.errno == 1:  # Operation not permitted
            print("Error: Raw sockets require root/administrator privileges.")

            return None
        raise

    # Generate a unique packet ID
    my_id = os.getpid() & 0xFFFF

    # Create ICMP header (type, code, checksum, id, sequence)
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, 0, my_id, 1)
    data = b"abcdefghijklmnopqrstuvwabcdefghi"  # Some dummy data

    # Calculate checksum
    chksum = checksum(header + data)
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, socket.htons(chksum), my_id, 1)
    packet = header + data
    time_sent = time.time()
    icmp_socket.sendto(packet, (dest_addr, 1))  # 1 is an arbitrary port for raw sockets

    # Wait for a reply
    while True:
        started_select = time.time()
        ready = select.select([icmp_socket], [], [], timeout)
        how_long_in_select = time.time() - started_select

        if ready[0] == []:  # Timeout
            icmp_socket.close()
            return None

        time_received = time.time()
        rec_packet, addr = icmp_socket.recvfrom(1024)

        # Parse ICMP header from the received packet
        icmp_header = rec_packet[20:28]  # IP header is usually 20 bytes
        type, code, checksum_reply, p_id, sequence = struct.unpack("bbHHh", icmp_header)

        if p_id == my_id:  # Check if it's our reply
            icmp_socket.close()

            return time_received - time_sent

        timeout -= how_long_in_select
        if timeout <= 0:
            icmp_socket.close()

            return None


def ping(host, count=4, timeout=1):
    """
    Pings the given host multiple times.
    """

    dest_addr = socket.gethostbyname(host)
    print(
        f"Pinging {host} [{dest_addr}] with {len(b'abcdefghijklmnopqrstuvwabcdefghi')} bytes of data:"
    )

    for i in range(count):
        delay = do_one_ping(dest_addr, timeout)

        if delay is None:
            print("Request timed out.")
        else:
            delay_ms = round(delay * 1000, 2)
            print(f"Reply from {dest_addr}: time={delay_ms}ms")

        time.sleep(1)  # Wait a bit before sending the next ping


def get_host_address(hostname: str):
    return socket.gethostbyname(hostname)
