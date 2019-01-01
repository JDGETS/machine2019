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
rotated_servo = False
master = None
light_state = True
light_value = 0

JOYSTICK_IGNORE_THRESHOLD = 32000

# Robot Moving speed
forward_mov_speed = config.get_param('for_speed')
backwards_mov_speed = config.get_param('back_speed')
rotation_speed = config.get_param('rotation_speed')

servo_camera_front = config.get_param('servo_camera_front')
servo_camera_back = config.get_param('servo_camera_back')


luminosity_step = 255/5
luminosity = luminosity_step


def servo_180(state):

    servo_channel = config.get_param('servo_camera_channel')

    if state:
        gpio.set_servo_pulsewidth(servo_channel, servo_camera_front )
    else:
        gpio.set_servo_pulsewidth(servo_channel, servo_camera_back )

    master.after(500, lambda: gpio.set_servo_pulsewidth(config.get_param('servo_camera_channel'), 0))


def keydown(e):
    global x, y, z, r, light_state, light_value, rotated_servo
    k = e.char

    keys[e.char] = 1

    if e.char == 'l':
        if(light_state == True):
            light_value = 50
            light_state = False
        else:
            light_value = 0
            light_state = True
    elif e.char == 'm' and light_value <= 100:
        light_value += 5
    elif e.char == 'n' and light_value > 5:
        light_value -= 5

    gpio.set_PWM_dutycycle(5, light_value)

    if e.char == 'k':

        if rotated_servo:
            print "low"
            gpio.set_servo_pulsewidth(config.get_param('servo_camera_channel'), servo_camera_front)
            #gpio.hardware_PWM(19, 50, 100000) # 800Hz 25% dutycycle
        else:
            print "high"
            gpio.set_servo_pulsewidth(config.get_param('servo_camera_channel'), servo_camera_back)
            #gpio.hardware_PWM(19, 50, 900000) # 800Hz 25% dutycycle

        rotated_servo = not rotated_servo

        master.after(500, lambda: gpio.set_servo_pulsewidth(config.get_param('servo_camera_channel'), 0))
        

    if e.char == 'j':
        gpio.set_servo_pulsewidth(config.get_param('servo_camera_channel'), 0)


def write_pwm(pins, value):
    for pin in pins:
        if pin not in states or states[pin] != value:
            states[pin] = value

            #print ('write', pin, value)
            gpio.set_PWM_dutycycle(pin, value)


def keyup(e):
    if e.char in keys:
        del keys[e.char]


def main():
    global luminosity, gpio, w, running, master

    ip = config.get_param('ip') 
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
                break

            # #print("Pas de manette connectee")
            # for event in events:
            #
            #     # Controle d'evenements et actions avec les boutons
            #     if event.ev_type == "Key":
            #
            #         # Bouton A : rotation camera
            #         if event.code == 'BTN_SOUTH' and event.state == 1:
            #             global rotated_servo
            #             rotated_servo = not rotated_servo
            #             servo_180(rotated_servo)
            #             print "hello"
            #
            #         elif event.code == "BTN_TR":
            #             global luminosity
            #             luminosity += luminosity_step
            #             write_pwm(config.get_param('light_channel'), luminosity)
            #
            #         elif event.code == "BTN_TL":
            #             global luminosity
            #             luminosity -= luminosity_step
            #             write_pwm(config.get_param('light_channel'), luminosity)
            #
            #     # Controle du mouvement avec joysticks et trigger
            #     if event.ev_type == "Absolute":
            #
            #         # Si le right trigger est enfonce : controle du robot
            #         if event.code == "ABS_RZ" and event.state == 255:
            #             self.right_trigger = True
            #
            #         # Si le right trigger est relache
            #         elif event.code == "ABS_RZ" and event.state < 200:
            #             self.right_trigger = False
            #             if 'forward' in pad_keys:
            #                 del pad_keys['forward']
            #             if 'backward' in pad_keys:
            #                 del pad_keys['backward']
            #             if 'left' in pad_keys:
            #                 del pad_keys['left']
            #             if 'right' in pad_keys:
            #                 del pad_keys['right']
            #
            #         # left joystick Y
            #         elif event.code == "ABS_Y":
            #             if event.state > JOYSTICK_IGNORE_THRESHOLD and self.right_trigger:
            #                 if 'forward' in pad_keys:
            #                     del pad_keys['forward']
            #
            #                 pad_keys['backward'] = 1
            #
            #             elif event.state < -JOYSTICK_IGNORE_THRESHOLD and self.right_trigger:
            #                 if 'backward' in pad_keys:
            #                     del pad_keys['backward']
            #
            #                 pad_keys['forward'] = 1
            #
            #             else:
            #                 if 'forward' in pad_keys:
            #                     del pad_keys['forward']
            #                 if 'backward' in pad_keys:
            #                     del pad_keys['backward']
            #
            #         # right joystick X
            #         elif event.code == "ABS_RX":
            #             if event.state > JOYSTICK_IGNORE_THRESHOLD and self.right_trigger:
            #                 if 'left' in pad_keys:
            #                     del pad_keys['left']
            #
            #                 pad_keys['right'] = 1
            #
            #             elif event.state < -JOYSTICK_IGNORE_THRESHOLD and self.right_trigger:
            #                 if 'right' in pad_keys:
            #                     del pad_keys['right']
            #
            #                 pad_keys['left'] = 1
            #
            #             else:
            #                 if 'left' in pad_keys:
            #                     del pad_keys['left']
            #                 if 'right' in pad_keys:
            #                     del pad_keys['right']


class gpioloop(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.speed = 0
        self.state = 'stop'
        self.target_x = 0
        self.actual_x = 0

        self.acceleration_ratio = config.get_param('acceleration_ratio')

        self.motor_left_actual_speed = 0
        self.motor_left_target_speed = 0

        self.motor_right_actual_speed = 0
        self.motor_right_target_speed = 0

        self.states = {}

    def run(self):
        while running:
            if 'w' in keys or 'forward' in pad_keys:
                self.motor_left_target_speed = forward_mov_speed
                self.motor_right_target_speed = forward_mov_speed

            elif 'e' in keys:
                self.motor_right_target_speed = forward_mov_speed
                self.motor_left_target_speed = 0
            elif 'q' in keys:
                self.motor_left_target_speed = forward_mov_speed
                self.motor_right_target_speed = 0

            elif 's' in keys or 'backward' in pad_keys:
                self.motor_left_target_speed = -backwards_mov_speed
                self.motor_right_target_speed = -backwards_mov_speed

            elif 'd' in keys or 'right' in pad_keys:
                self.motor_left_target_speed = rotation_speed
                self.motor_right_target_speed = -rotation_speed

            elif 'a' in keys or 'left' in pad_keys:
                self.motor_left_target_speed = -rotation_speed
                self.motor_right_target_speed = rotation_speed

            elif 'z' in keys:
                self.motor_left_target_speed = -2*backwards_mov_speed
                self.motor_right_target_speed = -2*backwards_mov_speed

            else:
                self.motor_left_target_speed = 0
                self.motor_right_target_speed = 0

            dx_left = sign(int(self.motor_left_target_speed * 10) - int(self.motor_left_actual_speed * 10))
            dx_right = sign(int(self.motor_right_target_speed * 10) - int(self.motor_right_actual_speed * 10))

            self.motor_left_actual_speed += dx_left * self.acceleration_ratio
            self.motor_right_actual_speed += dx_right * self.acceleration_ratio

            # self.motor_left_actual_speed = self.motor_left_target_speed
            # self.motor_right_actual_speed = self.motor_right_target_speed

            self.motor_left_actual_speed =  int(self.motor_left_actual_speed * config.get_param('speed_motor_left')/100.0)
            self.motor_right_actual_speed = int(self.motor_right_actual_speed * config.get_param('speed_motor_right')/100.0)

            if self.motor_left_actual_speed < 0:
                write_pwm([config.get_param('motor_left_back_channel')], abs(self.motor_left_actual_speed))
                write_pwm([config.get_param('motor_left_for_channel')], 0)
            else:
                write_pwm([config.get_param('motor_left_for_channel')], self.motor_left_actual_speed)
                write_pwm([config.get_param('motor_left_back_channel')], 0)

            if self.motor_right_actual_speed < 0:
                write_pwm([config.get_param('motor_right_back_channel')], abs(self.motor_right_actual_speed))
                write_pwm([config.get_param('motor_right_for_channel')], 0)
            else:
                write_pwm([config.get_param('motor_right_for_channel')], self.motor_right_actual_speed)
                write_pwm([config.get_param('motor_right_back_channel')], 0)

            time.sleep(1/60.0)


if __name__ == '__main__':
    main()
