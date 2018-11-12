import pigpio
import math
import rpyc

# Rpi names
rpi_green = "rPiGreen"
rpi_green_addr = "10.16.50.140"
rpi_pink = "raspberry-rose"
rpi_blue = "rPiBlue"
rpi_blue_addr = "10.0.0.2"
rpi_doggo_addr = "10.16.50.140"

# Rpc connection
RPC_PORT = 31000

# Controller constants
max_controller_value = 32767.0
x_ignore_treshold = 3000
y_ignore_treshold = 3000

# PWM Range
pwm_range = 255
pwm_half_range = 127

# PWM channels
MOTOR_RIGHT_FOR_CHANNEL = 22
MOTOR_LEFT_FOR_CHANNEL = 17
MOTOR_RIGHT_BACK_CHANNEL = 10
MOTOR_LEFT_BACK_CHANNEL = 27
MOTOR_FREQ_HZ = 100

MOTOR_FL_CHANNEL = 0
MOTOR_BL_CHANNEL = 1
MOTOR_FR_CHANNEL = 2
MOTOR_BR_CHANNEL = 3

# Choosing the robot to control
PUPPER = 'pupper'
DOGGO = 'doggo'

# Control modes
forward = 0
backwards = 1


class MotionController:
    def __init__(self):
        self.pwm_controller = PWMController(rpi_doggo_addr)
        self.acceleration_value = 0.1
        # self.rpc_connection = rpyc.connect(rpi_green_addr, RPC_PORT)

    def control_handle(self, controller_state, robot):
        # Mode de contrôle manuel du bras
        if controller_state.leftTrigger == 1 and robot == DOGGO:
            self.doggo_arm_control(controller_state)

        # Controle manuel de la propulsion
        if controller_state.rightTrigger == 1 and robot == DOGGO:
            self.doggo_motion_control(controller_state)

        if controller_state.rightTrigger == 1 and robot == PUPPER:
            self.pupper_motion_control(controller_state)

        # Arrêt de la propulsion
        if controller_state.rightTrigger == 0:
            self.pwm_controller.stop_all_motors()

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
        # Todo : implement server side
        pose = {'pose': [-x_s, y_s, -z_s, 0, 0, 0]}
        # self.rpc_connection.root.manual_move(pose)

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

        # print(tracks_msg)
        self.pwm_controller.doggo_pwm_motors(tracks_msg)

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
            forward_right = self.acceleration_function(int(abs(right)))
            backward_right = 0
        elif right < 0:
            forward_right = 0
            backward_right = self.acceleration_function(int(abs(right)))
        else:
            backward_right = 0
            forward_right = 0

        if left > 0:
            forward_left = self.acceleration_function(int(abs(left)))
            backward_left = 0
        elif left < 0:
            forward_left = 0
            backward_left = self.acceleration_function((abs(left)))
        else:
            backward_left = 0
            forward_left = 0

        tracks_msg = {'forward_right_pwm': forward_right, 'forward_left_pwm': forward_left,
                      'backward_right_pwm': backward_right, 'backward_left_pwm': backward_left}

        print(tracks_msg)
        self.pwm_controller.pupper_pwm_motors(tracks_msg)

    def acceleration_function(self, value):
        # TODO : arranger et implementer rampe acceleration
        if value > pwm_half_range:
            log = math.log10(value / pwm_range)
            new_value = pwm_half_range + 128 * (1.0 - abs(log))

        else:
            new_value = value

        return int(new_value)


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
                    self.rpi.set_PWM_dutycycle(MOTOR_LEFT_FOR_CHANNEL, int((1.0 - msg['forward_left_pwm']) * 255))
                else:
                    self.rpi.set_PWM_dutycycle(MOTOR_LEFT_FOR_CHANNEL, 0)
                    self.rpi.set_PWM_dutycycle(MOTOR_LEFT_BACK_CHANNEL, int((1.0 - msg['backward_left_pwm']) * 255))

            elif 'forward_left_pwm' in msg:
                self.rpi.set_PWM_dutycycle(MOTOR_LEFT_BACK_CHANNEL, 0)
                self.rpi.set_PWM_dutycycle(MOTOR_LEFT_FOR_CHANNEL, int((1.0 - msg['forward_left_pwm']) * 255))

            elif 'backward_left_pwm' in msg:
                self.rpi.set_PWM_dutycycle(MOTOR_LEFT_FOR_CHANNEL, 0)
                self.rpi.set_PWM_dutycycle(MOTOR_LEFT_BACK_CHANNEL, int((1.0 - msg['backward_left_pwm']) * 255))

            if 'forward_right_pwm' in msg and 'backward_right_pwm' in msg:
                if msg['forward_right_pwm'] > msg['backward_right_pwm']:
                    self.rpi.set_PWM_dutycycle(MOTOR_RIGHT_BACK_CHANNEL, 0)
                    self.rpi.set_PWM_dutycycle(MOTOR_RIGHT_FOR_CHANNEL, int((1.0 - msg['forward_right_pwm']) * 255))

                else:
                    self.rpi.set_PWM_dutycycle(MOTOR_RIGHT_FOR_CHANNEL, 0)
                    self.rpi.set_PWM_dutycycle(MOTOR_RIGHT_BACK_CHANNEL, int((1.0 - msg['backward_right_pwm']) * 255))

            elif 'forward_right_pwm' in msg:
                self.rpi.set_PWM_dutycycle(MOTOR_RIGHT_BACK_CHANNEL, 0)
                self.rpi.set_PWM_dutycycle(MOTOR_RIGHT_FOR_CHANNEL, int((1.0 - msg['forward_right_pwm']) * 255))

            elif 'backward_right_pwm' in msg:
                self.rpi.set_PWM_dutycycle(MOTOR_RIGHT_FOR_CHANNEL, 0)
                self.rpi.set_PWM_dutycycle(MOTOR_RIGHT_BACK_CHANNEL, int((1.0 - msg['backward_right_pwm']) * 255))


# For testing purposes
if __name__ == "__main__":
    controller = PWMController(rpi_green_addr)
    controller.test()
