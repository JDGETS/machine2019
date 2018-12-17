# coding=utf-8
from Tkinter import *
import pigpio
import inputs
from inputs import get_gamepad
from threading import Thread
import time

MOTOR_RIGHT_FOR_CHANEL = 27
MOTOR_RIGHT_BACK_CHANEL = 17
MOTOR_LEFT_FOR_CHANEL = 13
MOTOR_LEFT_BACK_CHANEL = 12

SOLENOID_SERVO = 22

JOYSTICK_IGNORE_THRESHOLD = 32000

pi_hostname = 'doggo-control'
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

pad_keys = {}

# States of the used pins
states = {}


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


def write_pwm(pins, value):
    for pin in pins:
        if pin not in states or states[pin] != value:
            states[pin] = value

            print ('write', pin, value)
        gpio.set_PWM_dutycycle(pin, value)


class gamepadloop(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.right_trigger = False

    def run(self):

        while running:

            events =[]

            try:
                events = get_gamepad()
            except inputs.UnpluggedError:
                print("Pas de manette connectée")

            for event in events:

                    # Controle d'evenements et actions avec les boutons
                    if event.ev_type == "Key":

                        # Bouton A : solenoide
                        if event.code == 'BTN_SOUTH':
                            write_pwm([SOLENOID_SERVO], 10 * event.state)

                    # Controle du mouvement avec joysticks et trigger
                    if event.ev_type == "Absolute":

                        # Si le right trigger est enfonce
                        if event.code == "ABS_RZ" and event.state == 255:
                            self.right_trigger = True

                        # Si le right trigger est relache
                        elif event.code == "ABS_RZ" and event.state < 200:
                            self.right_trigger = False
                            if 'forward' in pad_keys:
                                del pad_keys['forward']
                            if 'backward' in pad_keys:
                                del pad_keys['backward']
                            if 'left' in pad_keys:
                                del pad_keys['left']
                            if 'right' in pad_keys:
                                del pad_keys['right']

                        # left joystick Y
                        elif event.code == "ABS_Y":
                            if event.state > JOYSTICK_IGNORE_THRESHOLD and self.right_trigger:
                                if 'forward' in pad_keys:
                                    del pad_keys['forward']

                                pad_keys['backward'] = 1

                            elif event.state < -JOYSTICK_IGNORE_THRESHOLD and self.right_trigger:
                                if 'backward' in pad_keys:
                                    del pad_keys['backward']

                                pad_keys['forward'] = 1

                            else:
                                if 'forward' in pad_keys:
                                    del pad_keys['forward']
                                if 'backward' in pad_keys:
                                    del pad_keys['backward']

                        elif event.code == "ABS_RX":  # right joystick X
                            if event.state > JOYSTICK_IGNORE_THRESHOLD and self.right_trigger:
                                if 'left' in pad_keys:
                                    del pad_keys['left']

                                pad_keys['right'] = 1

                            elif event.state < -JOYSTICK_IGNORE_THRESHOLD and self.right_trigger:
                                if 'right' in pad_keys:
                                    del pad_keys['right']

                                pad_keys['left'] = 1

                            else:
                                if 'left' in pad_keys:
                                    del pad_keys['left']
                                if 'right' in pad_keys:
                                    del pad_keys['right']


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
            if 'w' in keys or 'forward' in pad_keys:
                self.state = 'forward'
                self.motor_left_target_speed = 120
                self.motor_right_target_speed = 120

            elif 's' in keys or 'backward' in pad_keys:
                self.state = 'backward'
                self.motor_left_target_speed = -120
                self.motor_right_target_speed = -120

            elif 'd' in keys or 'right' in pad_keys:
                self.state = 'right'
                self.motor_left_target_speed = 120
                self.motor_right_target_speed = -120

            elif 'a' in keys or 'left' in pad_keys:
                self.state = 'left'
                self.motor_right_target_speed = 120
                self.motor_left_target_speed = -120

            else:
                self.state = 'stop'
                self.motor_left_target_speed = 0
                self.motor_right_target_speed = 0

            dx_left = sign(int(self.motor_left_target_speed * 10) - int(self.motor_left_actual_speed * 10))
            dx_right = sign(int(self.motor_right_target_speed * 10) - int(self.motor_right_actual_speed * 10))

            self.motor_left_actual_speed += dx_left * 5
            self.motor_right_actual_speed += dx_right * 5

            print self.state

            # eased_x = int(100 * ease_in_out_quad(self.actual_x / 100.0))

            if self.motor_left_actual_speed < 0:
                write_pwm([MOTOR_LEFT_BACK_CHANEL], abs(self.motor_left_actual_speed))
                write_pwm([MOTOR_LEFT_FOR_CHANEL], 0)
            else:
                write_pwm([MOTOR_LEFT_FOR_CHANEL], self.motor_left_actual_speed)
                write_pwm([MOTOR_LEFT_BACK_CHANEL], 0)

            if self.motor_right_actual_speed < 0:
                write_pwm([MOTOR_RIGHT_BACK_CHANEL], abs(self.motor_right_actual_speed))
                write_pwm([MOTOR_RIGHT_FOR_CHANEL], 0)
            else:
                write_pwm([MOTOR_RIGHT_FOR_CHANEL], self.motor_right_actual_speed)
                write_pwm([MOTOR_RIGHT_BACK_CHANEL], 0)

            time.sleep(1/60.0)


t1 = gamepadloop()
t1.start()

t = gpioloop()
t.start()


try:
    mainloop()
except:
    pass

running = False

t1.join()
t.join()

# pi.disable_all()
