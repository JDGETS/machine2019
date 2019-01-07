import socket
from contextlib import closing
import os


def host_ready(host, port=22):
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.settimeout(0.250) # 250 ms

        return sock.connect_ex((host, port)) == 0


def wait_for_host(host, port=22):
    while not host_ready(host, port):
        print '.'


def sign(x):
    if x < 0:
        return -1
    if x > 0:
        return 1

    return 0

def map_to(value, istart, istop, ostart, ostop):
    return 1.0*ostart + (1.0*ostop - 1.0*ostart) * ((1.0*value - 1.0*istart) / (1.0*istop - 1.0*istart))


def clamp(value, lower, upper):
    if value < lower:
        return lower

    if value > upper:
        return upper

    return value



def spawn_camera(ip):
    stream_cmd = "mplayer -fps 200 -demuxer h264es ffmpeg://tcp://%s:9999 > /dev/null &"

    os.system(stream_cmd % ip)
