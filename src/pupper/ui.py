import config
import pigpio
import inputs
from inputs import get_gamepad
import time
from Tkinter import *
from threading import Thread
from utils import sign

gpio = None
w = None

running = True
label_vars = {}
keys = {}
pad_keys = {}
states = {}
grip_state = True

JOYSTICK_IGNORE_THRESHOLD = 32000

# Robot Moving speed
forward_mov_speed = 150
backwards_mov_speed = 120
rotation_speed = 120

luminosity_step = 255/5
luminosity = luminosity_step


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


def write_pwm(pins, value):
    for pin in pins:
        if pin not in states or states[pin] != value:
            states[pin] = value

            print ('write', pin, value)
            gpio.set_PWM_dutycycle(pin, value)


def keyup(e):
    if e.char in keys:
        del keys[e.char]


def main():
    global luminosity, gpio, w, running

    ip = config.pupper1_ip
    gpio = pigpio.pi(ip)

    master = Tk()

    w = Canvas(master, width=500, height=500)
    w.pack()

    master.bind("<KeyPress>", keydown)
    master.bind("<KeyRelease>", keyup)

    t = gpioloop()
    t.start()

    t1 = gamepadloop()
    t1.start()

    mainloop()

    running = False

    t.join()
    t1.join()


class gamepadloop(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.right_trigger = False
        self.left_trigger = False

    def run(self):

        while running:

            events =[]

            try:
                events = get_gamepad()
            except inputs.UnpluggedError:
                print("Pas de manette connectee")

            for event in events:

                    # Controle d'evenements et actions avec les boutons
                    if event.ev_type == "Key":

                        # Bouton A : rotation camera
                        if event.code == 'BTN_SOUTH':
                            pass # TODO : rotation de la camera

                        elif event.code == "BTN_TR":
                            global luminosity
                            luminosity += luminosity_step
                            write_pwm(config.pupper1_light_channel, luminosity)

                        elif event.code == "BTN_TL":
                            global luminosity
                            luminosity -= luminosity_step
                            write_pwm(config.pupper1_light_channel, luminosity)

                    # Controle du mouvement avec joysticks et trigger
                    if event.ev_type == "Absolute":

                        # Si le right trigger est enfonce : controle du robot
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

                        # right joystick X
                        elif event.code == "ABS_RX":
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
                self.motor_left_target_speed = forward_mov_speed
                self.motor_right_target_speed = forward_mov_speed

            elif 's' in keys or 'backward' in pad_keys:
                self.state = 'backward'
                self.motor_left_target_speed = -backwards_mov_speed
                self.motor_right_target_speed = -backwards_mov_speed

            elif 'd' in keys or 'right' in pad_keys:
                self.state = 'right'
                self.motor_left_target_speed = rotation_speed
                self.motor_right_target_speed = -rotation_speed

            elif 'a' in keys or 'left' in pad_keys:
                self.state = 'left'
                self.motor_left_target_speed = -rotation_speed
                self.motor_right_target_speed = rotation_speed

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
                write_pwm([config.pupper1_motor_left_back_channel], abs(self.motor_left_actual_speed))
                write_pwm([config.pupper1_motor_left_for_channel], 0)
            else:
                write_pwm([config.pupper1_motor_left_for_channel], self.motor_left_actual_speed)
                write_pwm([config.pupper1_motor_left_back_channel], 0)

            if self.motor_right_actual_speed < 0:
                write_pwm([config.pupper1_motor_right_back_channel], abs(self.motor_right_actual_speed))
                write_pwm([config.pupper1_motor_right_for_channel], 0)
            else:
                write_pwm([config.pupper1_motor_right_for_channel], self.motor_right_actual_speed)
                write_pwm([config.pupper1_motor_right_back_channel], 0)

            time.sleep(1/60.0)


if __name__ == '__main__':
    main()
