import config
import pigpio
import rpyc
import time

arm = None
gpio = None


def set_grip(state):
    if state:
        gpio.set_servo_pulsewidth(22, 1500)
    else:
        gpio.set_servo_pulsewidth(22, 1200)

    time.sleep(0.5)
    gpio.set_servo_pulsewidth(22, 0)


def main():
    global arm, gpio

    ip = config.get_param('control_ip')
    arm = rpyc.connect(ip, 18861).root
    gpio = pigpio.pi(ip)

    arm.set_grip(True)
