import config
import pigpio
import rpyc

arm = None
gpio = None

def main():
    global arm, gpio

    ip = config.get_param('control_ip')
    arm = rpyc.connect(ip, 18861).root
    gpio = pigpio.pi(ip)
