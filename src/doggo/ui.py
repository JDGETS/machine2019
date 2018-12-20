import config
import pigpio
import rpyc
# import inputs
# from inputs import get_gamepad
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
pad_keys = {}
states = {}
arm_state = {'y': 200, 'z': 200, 'r': 0}  # Start position
grip_state = True

JOYSTICK_IGNORE_THRESHOLD = 32000

# Robot moving speed
forward_mov_speed = 180
backwards_mov_speed = 150
rotation_speed = 150

# Arm mov increments
arm_step = 2
arm_wrist_angle_step = 10


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

    if e.char == 'p':
        arm.disable_all()
        print arm.get_position()

    if e.char == 'b':
        arm.write_goal(605, 408, 772, 415)

    if e.char == 'n':
        arm.write_goal(605, 483, 771, 436)

    if e.char == 'm':
        arm.write_goal(469, 768, 341, 301, speed=[50, 50, 100, 50])

    if e.char == 'l':
        arm.write_goal(195, 415, 550, 193, speed=[50, 75, 50, 100])


def write_arm_rpc(y, z, r):
    if not y == arm_state['y'] or not z == arm_state['z']:
        arm_state['y'] = y
        arm_state['z'] = z
        arm_state['r'] = r

        print ('move arm to y :', y, ' z : ', z, ' r :', r)
        arm.goto2D(y, z, r)


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

                        # Bouton A : solenoide
                        if event.code == 'BTN_SOUTH' and event.state == 1:
                            global grip_state
                            grip_state = not grip_state
                            set_grip(grip_state)

                        if event.code == 'BTN_NORTH':
                            arm.disable_all()

                    # Controle du mouvement avec joysticks et trigger
                    if event.ev_type == "Absolute":

                        # Si le left trigger est enfonce : controle du bras
                        if event.code == "ABS_Z" and event.state == 255:
                            self.left_trigger = True

                        # Si le left trigger est relache
                        elif event.code == "ABS_Z" and event.state < 200:
                            self.left_trigger = False
                            if 'up_z' in pad_keys:
                                del pad_keys['up_z']
                            if 'down_z' in pad_keys:
                                del pad_keys['down_z']
                            if 'for_y' in pad_keys:
                                del pad_keys['for_y']
                            if 'back_y' in pad_keys:
                                del pad_keys['back_y']

                        # left joystick Y
                        elif event.code == "ABS_Y":
                            if event.state > JOYSTICK_IGNORE_THRESHOLD and self.left_trigger:
                                if 'back_y' in pad_keys:
                                    del pad_keys['back_y']

                                pad_keys['back_y'] = 1

                            elif event.state < -JOYSTICK_IGNORE_THRESHOLD and self.left_trigger:
                                if 'for_y' in pad_keys:
                                    del pad_keys['for_y']

                                pad_keys['for_y'] = 1

                            else:
                                if 'back_y' in pad_keys:
                                    del pad_keys['back_y']
                                if 'for_y' in pad_keys:
                                    del pad_keys['for_y']

                        elif event.code == "ABS_RY":  # right joystick Y
                            if event.state > JOYSTICK_IGNORE_THRESHOLD and self.left_trigger:
                                if 'down_z' in pad_keys:
                                    del pad_keys['down_z']

                                pad_keys['down_z'] = 1

                            elif event.state < -JOYSTICK_IGNORE_THRESHOLD and self.left_trigger:
                                if 'up_z' in pad_keys:
                                    del pad_keys['up_z']

                                pad_keys['up_z'] = 1

                            else:
                                if 'up_z' in pad_keys:
                                    del pad_keys['up_z']
                                if 'down_z' in pad_keys:
                                    del pad_keys['down_z']

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

                        elif event.code == 'ABS_HAT0X':
                            if event.state == 1 and self.right_trigger:
                                if 'rot_left' in pad_keys:
                                    del pad_keys['rot_left']

                                pad_keys['rot_right'] = 1

                            elif event.state == -1 and self.right_trigger:
                                if 'rot_right' in pad_keys:
                                    del pad_keys['rot_right']

                                pad_keys['rot_left'] = 1

                            elif event.state == 0 and self.right_trigger:
                                del pad_keys['rot_right']
                                del pad_keys['rot_left']

                        elif event.code == 'ABS_HAT0Y':
                            if event.state == 1 and self.right_trigger:
                                if 'wrist_down' in pad_keys:
                                    del pad_keys['wrist_down']

                                pad_keys['wrist_up'] = 1

                            elif event.state == -1 and self.right_trigger:
                                if 'wrist_up' in pad_keys:
                                    del pad_keys['wrist_up']

                                pad_keys['wrist_down'] = 1

                            elif event.state == 0 and self.right_trigger:
                                del pad_keys['wrist_down']
                                del pad_keys['wrist_up']


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

            arm_y = arm_state['y']
            arm_z = arm_state['z']
            arm_r = arm_state['r']

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

            elif 'for_y' in pad_keys:
                self.state = 'arm_forward'
                arm_y += arm_step

            elif 'back_y' in pad_keys:
                self.state = 'arm_backwards'
                arm_y -= arm_step

            elif 'up_z' in pad_keys:
                self.state = 'arm_up'
                arm_z += arm_step

            elif 'down_z' in pad_keys:
                self.state = 'arm_down'
                arm_z -= arm_step

            elif 'wrist_up' in pad_keys:  # Todo : max arm angle
                self.state = 'arm_wrist_up'
                arm_r += arm_wrist_angle_step

            elif 'wrist_down' in pad_keys:  # Todo : max arm angle
                self.state = 'arm_wrist_down'
                arm_r -= arm_wrist_angle_step

            else:
                self.state = 'stop'
                self.motor_left_target_speed = 0
                self.motor_right_target_speed = 0

            write_arm_rpc(arm_y, arm_z, arm_r)

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

            if 'o' in keys or 'rot_right' in pad_keys:
                self.set_base_direction(1)
            elif 'i' in keys or 'rot_left' in pad_keys:
                self.set_base_direction(-1)
            else:
                self.set_base_direction(0)

            time.sleep(1/60.0)

    def set_base_direction(self, direction):
        if self.base_direction != direction:
            arm.move_base(direction)
            self.base_direction = direction


if __name__ == '__main__':
    main()
