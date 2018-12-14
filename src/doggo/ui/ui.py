from Tkinter import *
import rpyc
import math
import random
import pigpio
from threading import Thread
import time

MOTOR_RIGHT_FOR_CHANEL = 27
MOTOR_RIGHT_BACK_CHANEL = 17
MOTOR_LEFT_FOR_CHANEL = 22
MOTOR_LEFT_BACK_CHANEL = 26


pi_hostname = 'raspberrypi-vert'
# pi = rpyc.connect(pi_hostname, 18861).root
gpio = pigpio.pi(pi_hostname)

x = 200
y = 0
z = 300
r = 0
step = 20

master = Tk()

w = Canvas(master, width=500, height=500)
w.pack()

speed = 200

light_state = True

keys = {}

def sign(x):
    if x < 0:
        return -1
    if x > 0:
        return 1

    return 0

def keydown(e):
    global x, y, z, r, light_state
    k = e.char

    keys[e.char] = 1

    if k == 'l':

        if light_state:
            gpio.set_PWM_dutycycle(10, 50)
        else:
            gpio.set_PWM_dutycycle(10, 0)


        light_state = not light_state


def keyup(e):
    if e.char in keys:
        del keys[e.char]


master.bind("<KeyPress>", keydown)
master.bind("<KeyRelease>", keyup)

running = True

def ease_in_out_quad(t):
    if t < 0.5:
        return 2 * t * t
    return (-2 * t * t) + (4 * t) - 1

class gpioloop(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.speed = 0
        self.state = 'stop'
        self.target_x = 0
        self.actual_x = 0

        self.motor_left_actual_speed = 0
        self.motor_left_target_speed = 0

        self.motor_right_actual_speed = 0
        self.motor_right_target_speed = 0


        self.states = {}

    def run(self):
        while running:
            if 'w' in keys:
                self.state = 'forward'
                self.motor_left_target_speed = 100
                self.motor_right_target_speed = 100

            elif 's' in keys:
                self.state = 'backward'
                self.motor_left_target_speed = -80
                self.motor_right_target_speed = -80

            elif 'd' in keys:
                self.state = 'right'
                self.motor_left_target_speed = 50
                self.motor_right_target_speed = -50

            elif 'a' in keys:
                self.state = 'left'
                self.motor_left_target_speed = -50
                self.motor_right_target_speed = 50
            else:
                self.state = 'stop'
                self.motor_left_target_speed = 0
                self.motor_right_target_speed = 0


            dx_left = sign(int(self.motor_left_target_speed * 10) - int(self.motor_left_actual_speed * 10))
            dx_right = sign(int(self.motor_right_target_speed * 10) - int(self.motor_right_actual_speed * 10))

            self.motor_left_actual_speed += dx_left * 5
            self.motor_right_actual_speed += dx_right * 5

            # eased_x = int(100 * ease_in_out_quad(self.actual_x / 100.0))

            if self.motor_left_actual_speed < 0:
                self.write_pwm([MOTOR_LEFT_BACK_CHANEL], abs(self.motor_left_actual_speed))
                self.write_pwm([MOTOR_LEFT_FOR_CHANEL], 0)
            else:
                self.write_pwm([MOTOR_LEFT_FOR_CHANEL], self.motor_left_actual_speed)
                self.write_pwm([MOTOR_LEFT_BACK_CHANEL], 0)

            if self.motor_right_actual_speed < 0:
                self.write_pwm([MOTOR_RIGHT_BACK_CHANEL], abs(self.motor_right_actual_speed))
                self.write_pwm([MOTOR_RIGHT_FOR_CHANEL], 0)
            else:
                self.write_pwm([MOTOR_RIGHT_FOR_CHANEL], self.motor_right_actual_speed)
                self.write_pwm([MOTOR_RIGHT_BACK_CHANEL], 0)


            time.sleep(1/60.0)

    def write_pwm(self, pins, value):
        for pin in pins:
            if pin not in self.states or self.states[pin] != value:
                self.states[pin] = value

                print ('write', pin, value)
                gpio.set_PWM_dutycycle(pin, value)


t = gpioloop()
t.start()

try:
    mainloop()
except:
    pass

running = False

t.join()

# pi.disable_all()
