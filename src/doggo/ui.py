import config
import pigpio
import rpyc
import inputs
from inputs import get_gamepad
import time
from Tkinter import *
from threading import Thread
from utils import sign
from arm.state_manager import *

arm = None
gpio = None
w = None
sm = None
master = None

running = True
label_vars = {}
keys = {}
pad_keys = {}
states = {}
# arm_state = {'y': 200, 'z': 200, 'r': 0}  # Start position
grip_state = True

JOYSTICK_IGNORE_THRESHOLD = 32000

# Robot moving speed
forward_mov_speed = 150
backwards_mov_speed = 150
rotation_speed = 150

# Arm mov increments
arm_step = 5
arm_wrist_angle_step = 2


def set_grip(state):
    print 'grip state = ' + str(state)
    if state:
        gpio.set_servo_pulsewidth(22, 1500)
    else:
        gpio.set_servo_pulsewidth(22, 1200)

    master.after(500, lambda: gpio.set_servo_pulsewidth(22, 0))


def keydown(e):
    global x, y, z, r, light_state
    k = e.char

    keys[e.char] = 1

    if e.char == 'q':
        global grip_state
        grip_state = not grip_state
        set_grip(grip_state)

    if e.char == 'p':
        arm.disable_all()
        print arm.get_position()

    if e.char == 'c':
        print 'pickup'

    if e.char == 'v':
        print 'release'

    if e.char == 'x':
        print 'detetendre'
        arm.set_tyro_manager_state('detendre')

    if e.char == 'z':
        print 'tendre'
        arm.set_tyro_manager_state('tendre')


def write_pwm(pins, value):
    for pin in pins:
        if pin not in states or states[pin] != value:
            states[pin] = value

            print ('write', pin, value)
            gpio.set_PWM_dutycycle(pin, value)


def keyup(e):
    if e.char in keys:
        del keys[e.char]


def handle_apporter_tyro():
    sm.set_state(ArmPickupState())


def handle_lacher():
    sm.set_state(ArmReleaseState())


def handle_stop():
    sm.stop()


def handle_home():
    sm.stop()

def handle_crochet(number):
    def handler():
        sm.set_state(PickupCrochetState(number))

    return handler


def main():
    global arm, gpio, master, running, sm

    ip = config.get_param('control_ip')
    arm = rpyc.connect(ip, 18861).root
    gpio = pigpio.pi(ip)

    master = Tk()

    # w = Canvas(master, width=500, height=500)
    # w.pack()

    Label(master, text="MOUVEMENTS", bg="BLACK", fg="white").grid(row=1, column=0)

    Button(master, text="STOP", command=handle_stop).grid(row=2, column=0)
    Button(master, text="Apporter a tyrolienne", command=handle_apporter_tyro).grid(row=2, column=1)
    Button(master, text="Lacher", command=handle_lacher).grid(row=2, column=2)
    Button(master, text="Home", command=handle_home).grid(row=2, column=3)

    Label(master, text="CROCHETS", bg="BLACK", fg="white").grid(row=3, column=0)
    for i in range(4):
        Button(master, width=10, text=str(1 + i), command=handle_crochet(i + 1)).grid(row=4 + i, column=0)
        Button(master, width=10, text=str(i + 4 + 1), command=handle_crochet(i + 1 + 4)).grid(row=4 + i, column=1)


    master.bind("<KeyPress>", keydown)
    master.bind("<KeyRelease>", keyup)

    t = gpioloop()
    t.start()

    t1 = gamepadloop()
    t1.start()

    sm = ArmStateManager(arm, keys, gpio)
    sm.start()

    mainloop()

    sm.running = False
    running = False

    t.join()
    t1.join()
    sm.join()


class gamepadloop(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.right_trigger = False
        self.left_trigger = False

    def run(self):

        while running:

            events = []

            try:
                events = get_gamepad()
            except inputs.UnpluggedError:
                print("Pas de manette connectee")
                break


            for event in events:

                    # Controle d'evenements et actions avec les boutons
                    if event.ev_type == "Key":

                        # Bouton A : solenoide
                        if event.code == 'BTN_SOUTH' and event.state == 1:
                            global grip_state
                            grip_state = not grip_state
                            set_grip(grip_state)

                        # Bouton Y : mode tendre la tyro
                        if event.code == 'BTN_WEST' and event.state == 1:
                            arm.set_tyro_manager_state('tendre')

                        # Bouton B : mode detendre la tyro lorsque tension
                        if event.code == 'BTN_EAST' and event.state == 1:
                            arm.set_tyro_manager_state('detendre')

                        if event.code == "BTN_TR" and self.left_trigger:

                            if event.state == 1:
                                if 'i' in keys:
                                    del keys['i']

                                keys['o'] = 1

                            if event.state == 0:
                                del keys['o']

                        if event.code == "BTN_TL" and self.left_trigger:

                            if event.state == 1:
                                if 'o' in keys:
                                    del keys['o']

                                keys['i'] = 1

                            if event.state == 0:
                                del keys['i']

                    # Controle du mouvement avec joysticks et trigger
                    if event.ev_type == "Absolute":

                        # Si le left trigger est enfonce : controle du bras, utilisation du
                        # dictionnaire keys pour le state_manager
                        if event.code == "ABS_Z" and event.state == 255:
                            self.left_trigger = True

                        # Si le left trigger est relache
                        elif event.code == "ABS_Z" and event.state < 200:
                            self.left_trigger = False
                            if 'y' in keys:
                                del keys['y']
                            if 'h' in keys:
                                del keys['h']
                            if 't' in keys:
                                del keys['t']
                            if 'g' in keys:
                                del keys['g']
                            if 'i' in keys:
                                del keys['i']
                            if 'o' in keys:
                                del keys['o']
                            if 'u' in keys:
                                del keys['u']
                            if 'j' in keys:
                                del keys['j']

                        # left joystick Y
                        elif event.code == "ABS_Y":
                            if event.state > JOYSTICK_IGNORE_THRESHOLD and self.left_trigger:
                                if 't' in keys:
                                    del keys['t']

                                keys['g'] = 1

                            elif event.state < -JOYSTICK_IGNORE_THRESHOLD and self.left_trigger:
                                if 'g' in keys:
                                    del keys['g']

                                keys['t'] = 1

                            else:
                                if 't' in keys:
                                    del keys['t']
                                if 'g' in keys:
                                    del keys['g']

                        elif event.code == "ABS_RY":  # right joystick Y
                            if event.state > JOYSTICK_IGNORE_THRESHOLD and self.left_trigger:
                                if 'y' in keys:
                                    del keys['y']

                                keys['h'] = 1

                            elif event.state < -JOYSTICK_IGNORE_THRESHOLD and self.left_trigger:
                                if 'h' in keys:
                                    del keys['h']

                                keys['y'] = 1

                            else:
                                if 'y' in keys:
                                    del keys['y']
                                if 'h' in keys:
                                    del keys['h']

                        elif event.code == 'ABS_HAT0Y':
                            if event.state == -1 and self.left_trigger:
                                if 'j' in keys:
                                    del keys['j']

                                keys['u'] = 1

                            elif event.state == 1 and self.left_trigger:
                                if 'u' in keys:
                                    del keys['u']

                                keys['j'] = 1

                            elif event.state == 0 and self.left_trigger:
                                if 'u' in keys:
                                    del keys['u']
                                if 'j' in keys:
                                    del keys['j']

                        # Si le right trigger est enfonce : controle du robot, utilisation du
                        # dictionnaire pad_keys
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

                                print 'right'
                                pad_keys['right'] = 1

                            elif event.state < -JOYSTICK_IGNORE_THRESHOLD and self.right_trigger:
                                if 'right' in pad_keys:
                                    del pad_keys['right']

                                print 'left'
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

        self.base_direction = 0

    def run(self):
        while running:

            if 'w' in keys or 'forward' in pad_keys:
                self.motor_left_target_speed = forward_mov_speed
                self.motor_right_target_speed = forward_mov_speed

            elif 's' in keys or 'backward' in pad_keys:
                self.motor_left_target_speed = -backwards_mov_speed
                self.motor_right_target_speed = -backwards_mov_speed

            elif 'd' in keys or 'right' in pad_keys:
                self.motor_left_target_speed = rotation_speed
                self.motor_right_target_speed = -rotation_speed

            elif 'a' in keys or 'left' in pad_keys:
                self.motor_left_target_speed = -rotation_speed
                self.motor_right_target_speed = rotation_speed
            else:
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
                write_pwm([config.doggo_motor_left_back_channel], abs(self.motor_left_actual_speed))
                write_pwm([config.doggo_motor_left_for_channel], 0)
            else:
                write_pwm([config.doggo_motor_left_for_channel], self.motor_left_actual_speed)
                write_pwm([config.doggo_motor_left_back_channel], 0)

            if self.motor_right_actual_speed < 0:
                write_pwm([config.doggo_motor_right_back_channel], abs(self.motor_right_actual_speed))
                write_pwm([config.doggo_motor_right_for_channel], 0)
            else:
                write_pwm([config.doggo_motor_right_for_channel], self.motor_right_actual_speed)
                write_pwm([config.doggo_motor_right_back_channel], 0)


            time.sleep(1/60.0)


if __name__ == '__main__':
    main()
