from Tkinter import *
import rpyc
import math
import random
import pigpio

MOTOR_RIGHT_FOR_CHANNEL = 27
MOTOR_RIGHT_BACK_CHANNEL = 17
MOTOR_LEFT_FOR_CHANNEL = 13
MOTOR_LEFT_BACK_CHANNEL = 12


pi_hostname = 'raspberrypi-1'
pi = rpyc.connect(pi_hostname, 18861).root
gpio = pigpio.pi(pi_hostname)

x = 200
y = 0
z = 300
r = 0
step = 20

master = Tk()

w = Canvas(master, width=500, height=500)
w.pack()

def keydown(e):
    global x, y, z, r
    k = e.char

    if k == 'w':
        gpio.set_PWM_dutycycle(MOTOR_LEFT_FOR_CHANNEL, 255)
        gpio.set_PWM_dutycycle(MOTOR_RIGHT_FOR_CHANNEL, 255)

    if k == 's':
        gpio.set_PWM_dutycycle(MOTOR_LEFT_BACK_CHANNEL, 255)
        gpio.set_PWM_dutycycle(MOTOR_RIGHT_BACK_CHANNEL, 255)

    if k == 'k':
        pi.release()

    pi.goto(x, y, z, r, speed=50)


def keyup(e):
    gpio.set_PWM_dutycycle(MOTOR_RIGHT_FOR_CHANNEL, 0)
    gpio.set_PWM_dutycycle(MOTOR_RIGHT_BACK_CHANNEL, 0)
    gpio.set_PWM_dutycycle(MOTOR_LEFT_FOR_CHANNEL, 0)
    gpio.set_PWM_dutycycle(MOTOR_LEFT_BACK_CHANNEL, 0)


master.bind("<KeyPress>", keydown)
master.bind("<KeyRelease>", keyup)

mainloop()


pi.disable_all()
