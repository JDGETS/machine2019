import config
import pigpio
import rpyc
import time
from Tkinter import *
from threading import Thread
from utils import sign

arm = None
gpio = None
w = None

running = True
label_vars = {}
keys = {}
grip_state = True


def set_grip(state):
    if state:
        gpio.set_servo_pulsewidth(22, 1500)
    else:
        gpio.set_servo_pulsewidth(22, 1200)

    w.after(500, lambda: gpio.set_servo_pulsewidth(22, 0))


def keydown(e):
    global x, y, z, r, light_state
    k = e.char

    keys[e.char] = 1

    if e.char == 'g':
        global grip_state
        grip_state = not grip_state
        set_grip(grip_state)


def keyup(e):
    if e.char in keys:
        del keys[e.char]


def main():
    global arm, gpio, w, running

    ip = config.get_param('control_ip')
    arm = rpyc.connect(ip, 18861).root
    gpio = pigpio.pi(ip)

    master = Tk()

    w = Canvas(master, width=500, height=500)
    w.pack()

    master.bind("<KeyPress>", keydown)
    master.bind("<KeyRelease>", keyup)

    t = gpioloop()
    t.start()

    mainloop()

    running = False

    t.join()



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
                self.motor_left_target_speed = 200
                self.motor_right_target_speed = 200

            elif 's' in keys:
                self.state = 'backward'
                self.motor_left_target_speed = -80
                self.motor_right_target_speed = -80

            elif 'd' in keys:
                self.state = 'right'
                self.motor_left_target_speed = 150
                self.motor_right_target_speed = -150

            elif 'a' in keys:
                self.state = 'left'
                self.motor_left_target_speed = -150
                self.motor_right_target_speed = 150
            else:
                self.state = 'stop'
                self.motor_left_target_speed = 0
                self.motor_right_target_speed = 0


            dx_left = sign(int(self.motor_left_target_speed * 10) - int(self.motor_left_actual_speed * 10))
            dx_right = sign(int(self.motor_right_target_speed * 10) - int(self.motor_right_actual_speed * 10))

            # self.motor_left_actual_speed += dx_left * 10
            # self.motor_right_actual_speed += dx_right * 10

            # pas de rampe pour doggo, mais ma laisser ca ici en cas que il faudrait en avoir une
            self.motor_left_actual_speed = self.motor_left_target_speed
            self.motor_right_actual_speed = self.motor_right_target_speed

            if self.motor_left_actual_speed < 0:
                self.write_pwm([config.doggo_motor_left_back_channel], abs(self.motor_left_actual_speed))
                self.write_pwm([config.doggo_motor_left_for_channel], 0)
            else:
                self.write_pwm([config.doggo_motor_left_for_channel], self.motor_left_actual_speed)
                self.write_pwm([config.doggo_motor_left_back_channel], 0)

            if self.motor_right_actual_speed < 0:
                self.write_pwm([config.doggo_motor_right_back_channel], abs(self.motor_right_actual_speed))
                self.write_pwm([config.doggo_motor_right_for_channel], 0)
            else:
                self.write_pwm([config.doggo_motor_right_for_channel], self.motor_right_actual_speed)
                self.write_pwm([config.doggo_motor_right_back_channel], 0)


            time.sleep(1/60.0)

    def write_pwm(self, pins, value):
        for pin in pins:
            if pin not in self.states or self.states[pin] != value:
                self.states[pin] = value

                print ('write', pin, value)
                gpio.set_PWM_dutycycle(pin, value)
