# coding=utf-8
import pigpio
import math
import rpyc
import time

# Rpi names
rpi_green = "raspberrypi-1"
rpi_green_addr = "10.16.50.140"
rpi_pink = "raspberry-rose"
rpi_blue = "rPiBlue"
rpi_blue_addr = "10.0.0.2"
rpi_doggo_address = "192.168.0.160"

# Rpc connection
RPC_PORT = 31000

# Controller constants
max_controller_value = 32767.0
x_ignore_treshold = 3000
y_ignore_treshold = 3000

# PWM Range
pwm_range = 170
pwm_half_range = 127

# PWM channels
MOTOR_RIGHT_FOR_CHANNEL = 27
MOTOR_LEFT_FOR_CHANNEL = 26
MOTOR_RIGHT_BACK_CHANNEL = 22
MOTOR_LEFT_BACK_CHANNEL = 17
MOTOR_FREQ_HZ = 100

DOGGO_RIGHT_FOR_CHANNEL = 27
DOGGO_LEFT_FOR_CHANNEL = 13
DOGGO_RIGHT_BACK_CHANNEL = 17
DOGGO_LEFT_BACK_CHANNEL = 12
DOGGO_SOLENOID_CROCHET = 22

# Choosing the robot to control
PUPPER = 'pupper'
DOGGO = 'doggo'

# Control modes
forward = 0
backwards = 1


class MotionController:
    def __init__(self):
        self.acceleration_value = 0.1
        #self.pwm_controller = PWMController(rpi_doggo_hostname)
        # self.rpc_connection = rpyc.connect(rpi_green_addr, RPC_PORT)

        ### new control
        self.gpio = pigpio.pi(rpi_doggo_address)
        self.speed = 0
        self.state = 'stop'
        self.target_x = 0
        self.actual_x = 0

        self.motor_left_actual_speed = 0
        self.motor_left_target_speed = 0

        self.motor_right_actual_speed = 0
        self.motor_right_target_speed = 0

        self.states = {}
        ###

    def control_handle(self, controller_state, robot):
        # Mode de contrôle manuel du bras
        if controller_state.leftTrigger == 1 and robot == DOGGO:
            self.doggo_arm_control(controller_state)

        # Controle manuel de la propulsion
        if controller_state.rightTrigger == 1 and robot == DOGGO:
            self.new_doggo_control(controller_state)

        if controller_state.rightTrigger == 1 and robot == PUPPER:
            self.pupper_motion_control(controller_state)

        # Arrêt de la propulsion
        # if controller_state.rightTrigger == 0:
        #     self.pwm_controller.stop_all_motors()

    def new_doggo_control(self, controller_state):

        IGNORE_TRESHOLD = 3000.0

        if controller_state.leftJoyY >= IGNORE_TRESHOLD:
            self.state = 'forward'
            self.motor_left_target_speed = 130
            self.motor_right_target_speed = 130

        elif controller_state.leftJoyY <= -IGNORE_TRESHOLD:
            self.state = 'backward'
            self.motor_left_target_speed = -100
            self.motor_right_target_speed = -100

        elif controller_state.rightJoyY >= IGNORE_TRESHOLD:
            self.state = 'right'
            self.motor_left_target_speed = 80
            self.motor_right_target_speed = -80

        elif controller_state.rightJoyY <= -IGNORE_TRESHOLD:
            self.state = 'left'
            self.motor_left_target_speed = -80
            self.motor_right_target_speed = 80
        else:
            self.state = 'stop'
            self.motor_left_target_speed = 0
            self.motor_right_target_speed = 0

        dx_left = self.sign(int(self.motor_left_target_speed * 10) - int(self.motor_left_actual_speed * 10))
        dx_right = self.sign(int(self.motor_right_target_speed * 10) - int(self.motor_right_actual_speed * 10))

        self.motor_left_actual_speed += dx_left * 5
        self.motor_right_actual_speed += dx_right * 5

        # eased_x = int(100 * ease_in_out_quad(self.actual_x / 100.0))

        if self.motor_left_actual_speed < 0:
            self.write_pwm([DOGGO_LEFT_BACK_CHANNEL], abs(self.motor_left_actual_speed))
            self.write_pwm([DOGGO_LEFT_FOR_CHANNEL], 0)
        else:
            self.write_pwm([DOGGO_LEFT_FOR_CHANNEL], self.motor_left_actual_speed)
            self.write_pwm([DOGGO_LEFT_BACK_CHANNEL], 0)

        if self.motor_right_actual_speed < 0:
            self.write_pwm([DOGGO_RIGHT_BACK_CHANNEL], abs(self.motor_right_actual_speed))
            self.write_pwm([DOGGO_RIGHT_FOR_CHANNEL], 0)
        else:
            self.write_pwm([DOGGO_RIGHT_FOR_CHANNEL], self.motor_right_actual_speed)
            self.write_pwm([DOGGO_RIGHT_BACK_CHANNEL], 0)

        time.sleep(1 / 60.0)

    def sign(self, x):
        if x < 0:
            return -1
        if x > 0:
            return 1

        return 0

    def doggo_arm_control(self, controller_state):
        IGNORE_TRESHOLD = 3000
        # Get x motion
        if controller_state.leftJoyX > IGNORE_TRESHOLD:
            x_s = max(min(controller_state.leftJoyX / 32767.0, 1.), 0.0)
        elif controller_state.leftJoyX < -IGNORE_TRESHOLD:
            x_s = -max(min(abs(controller_state.leftJoyX / 32767.0), 1.), 0.0)
        else:
            x_s = 0.0
        # Get y motion
        if controller_state.leftJoyY > IGNORE_TRESHOLD:
            y_s = max(min(controller_state.leftJoyY / 32767.0, 1.), 0.0)
        elif controller_state.leftJoyY < -IGNORE_TRESHOLD:
            y_s = -max(min(abs(controller_state.leftJoyY / 32767.0), 1.), 0.0)
        else:
            y_s = 0.0
        # Get z motion
        if controller_state.rightJoyY > IGNORE_TRESHOLD:
            z_s = max(min(controller_state.rightJoyY / 32767.0, 1.), 0.0)
        elif controller_state.rightJoyY < -IGNORE_TRESHOLD:
            z_s = -max(min(abs(controller_state.rightJoyY / 32767.0), 1.), 0.0)
        else:
            z_s = 0.0

        # Client RPC to remote ArmModule
        pose = {'x': -x_s, 'y': y_s, 'z': -z_s}
        print pose
        # self.rpc_connection.root.move_to_pose(pose)

    # Même code que l'an passé - méthode tracks_ctrl() dans ControlModule
    def doggo_motion_control(self, controller_state):
        # Get y motion
        if controller_state.leftJoyY > 3000 or controller_state.leftJoyY < -3000:
            right = left = controller_state.leftJoyY / 32767.0

        else:
            right = left = 0

        # Get z motion
        if controller_state.rightJoyX > 5000:
            left = controller_state.rightJoyX / 32767.0
            right = -controller_state.rightJoyX / 32767.0

        elif controller_state.rightJoyX < -5000:
            left = controller_state.rightJoyX / 32767.0
            right = -controller_state.rightJoyX / 32767.0

        if right > 0:
            forward_right = min(abs(right + 0.5), 0.99)
            backward_right = 0
        elif right < 0:
            forward_right = 0
            backward_right = min(abs(right + 0.5), 0.99)
        else:
            backward_right = 0
            forward_right = 0

        if left > 0:
            forward_left = min(abs(left + 0.5), 0.99)
            backward_left = 0
        elif left < 0:
            forward_left = 0
            backward_left = min(abs(left + 0.5), 0.99)
        else:
            backward_left = 0
            forward_left = 0

        tracks_msg = {'forward_right_pwm': forward_right, 'forward_left_pwm': forward_left,
                      'backward_right_pwm': backward_right, 'backward_left_pwm': backward_left}

        if backward_right < 0.001:
            del tracks_msg['backward_right_pwm']

        if backward_left < 0.001:
            del tracks_msg['backward_left_pwm']

        if forward_left < 0.001:
            del tracks_msg['forward_left_pwm']

        if forward_right < 0.001:
            del tracks_msg['forward_right_pwm']

        if bool(tracks_msg) is False:
            tracks_msg = {'forward_right_pwm': 0, 'forward_left_pwm': 0, 'backward_right_pwm': 0,
                          'backward_left_pwm': 0}

        print(tracks_msg)
        # self.pwm_controller.doggo_pwm_motors(tracks_msg)

    # Code quelque peu différent que celui de l'année passée et refactored, mais fait la même chose pour le moment
    def pupper_motion_control(self, controller_state):
        if controller_state.leftJoyY > y_ignore_treshold or controller_state.leftJoyY < -y_ignore_treshold:
            right = left = pwm_range * controller_state.leftJoyY / max_controller_value

        else:
            right = left = 0

        # Get z motion

        if controller_state.rightJoyX > x_ignore_treshold:
            left = pwm_range * controller_state.rightJoyX / max_controller_value
            right = -pwm_range * controller_state.rightJoyX / max_controller_value

        elif controller_state.rightJoyX < -x_ignore_treshold:
            left = pwm_range * controller_state.rightJoyX / max_controller_value
            right = -pwm_range * controller_state.rightJoyX / max_controller_value

        if right > 0:
            forward_right = int(abs(right))
            backward_right = 0
        elif right < 0:
            forward_right = 0
            backward_right = int(abs(right))
        else:
            backward_right = 0
            forward_right = 0

        if left > 0:
            forward_left = int(abs(left))
            backward_left = 0
        elif left < 0:
            forward_left = 0
            backward_left = int(abs(left))
        else:
            backward_left = 0
            forward_left = 0

        tracks_msg = {'forward_right_pwm': forward_right, 'forward_left_pwm': forward_left,
                      'backward_right_pwm': backward_right, 'backward_left_pwm': backward_left}

        if backward_right < 2:
            del tracks_msg['backward_right_pwm']

        if backward_left < 2:
            del tracks_msg['backward_left_pwm']

        if forward_left < 2:
            del tracks_msg['forward_left_pwm']

        if forward_right < 2:
            del tracks_msg['forward_right_pwm']

        if bool(tracks_msg) is False:
            tracks_msg = {'forward_right_pwm': 0, 'forward_left_pwm': 0, 'backward_right_pwm': 0,
                          'backward_left_pwm': 0}

        print(tracks_msg)
        # self.pwm_controller.doggo_pwm_motors(tracks_msg)

    def write_pwm(self, pins, value):
        for pin in pins:
            if pin not in self.states or self.states[pin] != value:
                self.states[pin] = value

                print ('write', pin, value)
                self.gpio.set_PWM_dutycycle(pin, value)


class PWMController:
    def __init__(self, rpi_address):
        self.rpi = pigpio.pi(rpi_address)

    # Test pruposes
    def test(self):
        # self.rpi.set_mode(6, pigpio.OUTPUT)
        self.rpi.set_PWM_dutycycle(MOTOR_RIGHT_FOR_CHANNEL, 0)
        self.rpi.set_PWM_dutycycle(MOTOR_RIGHT_BACK_CHANNEL, 0)
        self.rpi.set_PWM_dutycycle(MOTOR_LEFT_FOR_CHANNEL, 0)
        self.rpi.set_PWM_dutycycle(MOTOR_LEFT_BACK_CHANNEL, 0)

    def stop_all_motors(self):
        self.rpi.set_PWM_dutycycle(MOTOR_RIGHT_FOR_CHANNEL, 0)
        self.rpi.set_PWM_dutycycle(MOTOR_LEFT_FOR_CHANNEL, 0)
        self.rpi.set_PWM_dutycycle(MOTOR_RIGHT_BACK_CHANNEL, 0)
        self.rpi.set_PWM_dutycycle(MOTOR_LEFT_BACK_CHANNEL, 0)

    # PWM control (remote gpio) for the Puppers
    def pupper_pwm_motors(self, msg):
        self.rpi.set_PWM_dutycycle(MOTOR_RIGHT_FOR_CHANNEL, msg['forward_right_pwm'])
        self.rpi.set_PWM_dutycycle(MOTOR_LEFT_FOR_CHANNEL, msg['forward_left_pwm'])
        self.rpi.set_PWM_dutycycle(MOTOR_RIGHT_BACK_CHANNEL, msg['backward_right_pwm'])
        self.rpi.set_PWM_dutycycle(MOTOR_LEFT_BACK_CHANNEL, msg['backward_left_pwm'])

    # PWM control (remote gpio) for Doggo
    def doggo_pwm_motors(self, msg):

        if 'forward_left_pwm' in msg and 'backward_left_pwm' in msg and 'forward_right_pwm' in msg and 'backward_right_pwm' in msg:

            self.rpi.set_PWM_dutycycle(MOTOR_RIGHT_FOR_CHANNEL, msg['forward_right_pwm'])
            self.rpi.set_PWM_dutycycle(MOTOR_LEFT_FOR_CHANNEL, msg['forward_left_pwm'])
            self.rpi.set_PWM_dutycycle(MOTOR_RIGHT_BACK_CHANNEL, msg['backward_right_pwm'])
            self.rpi.set_PWM_dutycycle(MOTOR_LEFT_BACK_CHANNEL, msg['backward_left_pwm'])

        else:
            if 'forward_left_pwm' in msg and 'backward_left_pwm' in msg:
                if msg['forward_left_pwm'] > msg['backward_left_pwm']:
                    self.rpi.set_PWM_dutycycle(MOTOR_LEFT_BACK_CHANNEL, 0)
                    self.rpi.set_PWM_dutycycle(MOTOR_LEFT_FOR_CHANNEL, msg['forward_left_pwm'])
                else:
                    self.rpi.set_PWM_dutycycle(MOTOR_LEFT_FOR_CHANNEL, 0)
                    self.rpi.set_PWM_dutycycle(MOTOR_LEFT_BACK_CHANNEL, msg['backward_left_pwm'])

            elif 'forward_left_pwm' in msg:
                self.rpi.set_PWM_dutycycle(MOTOR_LEFT_BACK_CHANNEL, 0)
                self.rpi.set_PWM_dutycycle(MOTOR_LEFT_FOR_CHANNEL, msg['forward_left_pwm'])

            elif 'backward_left_pwm' in msg:
                self.rpi.set_PWM_dutycycle(MOTOR_LEFT_FOR_CHANNEL, 0)
                self.rpi.set_PWM_dutycycle(MOTOR_LEFT_BACK_CHANNEL, msg['backward_left_pwm'])

            if 'forward_right_pwm' in msg and 'backward_right_pwm' in msg:
                if msg['forward_right_pwm'] > msg['backward_right_pwm']:
                    self.rpi.set_PWM_dutycycle(MOTOR_RIGHT_BACK_CHANNEL, 0)
                    self.rpi.set_PWM_dutycycle(MOTOR_RIGHT_FOR_CHANNEL, msg['forward_right_pwm'])

                else:
                    self.rpi.set_PWM_dutycycle(MOTOR_RIGHT_FOR_CHANNEL, 0)
                    self.rpi.set_PWM_dutycycle(MOTOR_RIGHT_BACK_CHANNEL, msg['backward_right_pwm'])

            elif 'forward_right_pwm' in msg:
                self.rpi.set_PWM_dutycycle(MOTOR_RIGHT_BACK_CHANNEL, 0)
                self.rpi.set_PWM_dutycycle(MOTOR_RIGHT_FOR_CHANNEL, msg['forward_right_pwm'])

            elif 'backward_right_pwm' in msg:
                self.rpi.set_PWM_dutycycle(MOTOR_RIGHT_FOR_CHANNEL, 0)
                self.rpi.set_PWM_dutycycle(MOTOR_RIGHT_BACK_CHANNEL, msg['backward_right_pwm'])


# For testing purposes
if __name__ == "__main__":
    controller = PWMController(rpi_green_addr)
    controller.test()
