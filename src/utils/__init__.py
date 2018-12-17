import socket
from contextlib import closing


def host_ready(host, port=22):
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.settimeout(0.250) # 250 ms

        return sock.connect_ex((host, port)) == 0


def wait_for_host(host, port=22):
    while not host_ready(host, port):
        print '.'
