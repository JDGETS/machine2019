from ik import ik
from dxl.dxlchain import DxlChain
from collections import namedtuple
import math
from threading import Thread
import time
import rpyc
import pigpio

USB_PORT = '/dev/ttyUSB0'

Point = namedtuple('Point', ['x', 'y', 'z', 'r'])


class TyroManager(Thread):
    def __init__(self, chain, motor_id=8):
        Thread.__init__(self)
        self.state = 'detendre'
        self.running = True
        self.chain = chain
        self.motor_id = motor_id
        self.speed = 512
        self.moving = False


    def run(self):
        self.chain.set_reg(self.motor_id, 'cw_angle_limit', 0)
        self.chain.set_reg(self.motor_id, 'ccw_angle_limit', 0)

        while self.running:
            if self.state == 'detendre':
                self.detendre()
            elif self.state == 'tendre':
                self.moving = False
                self.tendre()
            else:
                pass

            time.sleep(0.1)

    def detendre(self):
        load = self.chain.get_reg(self.motor_id, 'present_load')
        direction = load >> 10
        load = load % 1023

        if load >= 10:
            self.chain.set_reg(self.motor_id, 'moving_speed', self.speed)
            time.sleep(1)

            self.chain.set_reg(self.motor_id, 'moving_speed', 0)
            time.sleep(0.2)

    def tendre(self):
        speed = self.chain.get_reg(self.motor_id, 'present_speed') & 1023
        speed = (2 * direction - 1) * speed * 0.111

        if not self.moving:
            self.moving = True
            self.chain.set_reg(self.motor_id, 'moving_speed', self.speed + 1024)

        if abs(speed) <= 40:
            self.state = 'manuel'


def map_to(value, istart, istop, ostart, ostop):
    return 1.0*ostart + (1.0*ostop - 1.0*ostart) * ((1.0*value - 1.0*istart) / (1.0*istop - 1.0*istart))


def motors_to_angles(goal1, goal23, goal4, goal5):
    '''
    Converts motor positions to angles
    '''
    a1 = map_to(goal1, 826, 521, 0, 90)
    a23 = 180 - map_to(goal23, 227, 820, 10, 180)
    a4 = map_to(goal4, 804, 192, 0, 180)
    a5 = map_to(goal5, 213, 805, 90, -90)

    return (a1, a23, a4, a5)


def angles_to_motors(a1, a23, a4, a5):
    '''
    Converts angles to motor positions
    '''
    goal1 = map_to(a1, 0, 90, 826, 521)
    goal23 = map_to(180 - a23, 10, 180, 227, 820)
    goal4 = map_to(a4, 0, 180, 804, 192)
    goal5 = map_to(a5, 90, -90, 213, 805)

    return (goal1, goal23, goal4, goal5)


class Arm:
    def __init__(self, port=USB_PORT):
        self.port = port
        self.goal = Point(0, 0, 0, 0)
        self.opened = False
        self.pi = None


    def open(self):
        self.pi = pigpio.pi()
        self.dyn_chain = DxlChain(self.port, rate=1000000)
        self.dyn_chain.open()

        self.motors = self.dyn_chain.get_motor_list()

        assert len(self.motors) == 6, 'Some arm motors are missing. Expected 6 instead got %d' % len(self.motors)

        self.tyro_manager = TyroManager(self.dyn_chain)
        self.tyro_manager.start()

        self.opened = True

    def close(self):
        self.opened = False
        self.dyn_chain.close()

    def release(self):
        self.pi.set_PWM_dutycycle(22, 120)
        time.sleep(0.5)
        self.pi.set_PWM_dutycycle(22, 0)

    def goto2D(self, y, z, r, speed=50):
        '''
        Uses inverse kinematic to go to a position in planar space (only y and z)
        '''
        r = math.radians(r)
        self.goal = Point(0, y, z, r)

        joints = ik(*self.goal)
        joints = map(math.degrees, joints)
        goals = angles_to_motors(*joints)

        return self.write_goal_without_base(goals[1], goals[2], goals[3], speed=speed)

    def goto(self, x, y, z, r, speed=50):
        '''
        Uses inverse kinematic to go to a position in space
        '''
        r = math.radians(r)
        self.goal = Point(x, y, z, r)

        joints = ik(*self.goal)
        joints = map(math.degrees, joints)
        goals = angles_to_motors(*joints)

        return self.write_goal(*goals, speed=speed)

    def write_goal_without_base(self, goal23, goal4, goal5, speed=50):
        '''
        Write goal positions of all servos with given speed
        '''
        if not goal5 <= 200 and not goal5 >= 800:
            if isinstance(speed, list):
                s23, s4, s5 = speed
                self.dyn_chain.sync_write_pos_speed([2, 3, 4, 5], [goal23, 1023 - goal23, goal4, goal5], [s23, s23, s4, s5])
            else:
                self.dyn_chain.sync_write_pos_speed([2, 3, 4, 5], [goal23, 1023 - goal23, goal4, goal5], [speed]*5)

        elif goal5 <= 200:
            goal5 = 200
            if isinstance(speed, list):
                s23, s4, s5 = speed
                self.dyn_chain.sync_write_pos_speed([2, 3, 4, 5], [goal23, 1023 - goal23, goal4, goal5], [s23, s23, s4, s5])
            else:
                self.dyn_chain.sync_write_pos_speed([2, 3, 4, 5], [goal23, 1023 - goal23, goal4, goal5], [speed]*5)

        elif goal5 >= 800:
            goal5 = 800
            if isinstance(speed, list):
                s23, s4, s5 = speed
                self.dyn_chain.sync_write_pos_speed([2, 3, 4, 5], [goal23, 1023 - goal23, goal4, goal5], [s23, s23, s4, s5])
            else:
                self.dyn_chain.sync_write_pos_speed([2, 3, 4, 5], [goal23, 1023 - goal23, goal4, goal5], [speed]*5)

    def write_goal(self, goal1, goal23, goal4, goal5, speed=50):
        '''
        Write goal positions of all servos with given speed
        '''
        if isinstance(speed, list):
            s1, s23, s4, s5 = speed
            self.dyn_chain.sync_write_pos_speed([1, 2, 3, 4, 5], [goal1, goal23, 1023 - goal23, goal4, goal5], [s1, s23, s23, s4, s5])
        else:
            self.dyn_chain.sync_write_pos_speed([1, 2, 3, 4, 5], [goal1, goal23, 1023 - goal23, goal4, goal5], [speed]*5)

    def disable_all(self):
        '''
        Disable torque of all motors
        '''
        self.dyn_chain.disable()


    def move_base(self, direction, speed=30):
        '''
        Moves the base in the given direction at the given speed
        Direction = 1 / -1 for cw/ccw direction, 0 => stop
        '''

        if direction == 1:
            self.dyn_chain.goto(1, 0, speed=speed, blocking=False)
        elif direction == -1:
            self.dyn_chain.goto(1, 835, speed=speed, blocking=False)
        else:
            self.dyn_chain.disable(1)

    def get_angles(self):
        '''
        Estimates joints angle based on servos positions
        '''
        return motors_to_angles(*self.get_position())

    def get_position(self):
        '''
        Servos positions
        '''
        positions = self.dyn_chain.get_position()
        return (positions[1], positions[2], positions[4], positions[5])

    def motors_load(self):
        '''
        Ratio of maximal torque of each joints.
        A value of  0.5 means 50% of maximmal torque applied in clockwise direction
        A value of -0.25 means 25% of maximmal torque applied in counter-clockwise Direction

        Return value is (motor1, motor2, motor4, motor5)
        '''
        loads = []

        for i in [1, 2, 4, 5]:
            present_load = self.dyn_chain.get_reg(i, "present_load")
            ratio = (present_load & 1023) / 1023.0
            direction = ((present_load >> 10) & 1) * 2 - 1

            loads.append(ratio * direction)

        return loads

    def wait_stopped(self):
        '''
        Sleeps until all the motors reached their goals
        '''
        self.dyn_chain.wait_stopped([1, 2, 3, 4, 5])

    def stop_movement(self):
        '''
        Sets the goal to the current position of the motors
        '''
        positions = self.get_position()
        self.write_goal(*positions)

    def wait_stopped_sleep(self, sleep=time.sleep):
        '''
        Sleeps using the provided function until all the motors reached their goals
        '''
        ids = self.dyn_chain.get_motors([1, 2, 3, 4, 5])

        while True:
            moving = False
            for id in ids:
                if self.dyn_chain.get_reg(reg, 'moving') != 0:
                    moving = True
                    break
            if not moving:
                break

            sleep(0.1)

    def set_tyro_manager_state(self, state):
        self.tyro_manager.state = state


def main_test_crochets():

    arm = Arm()
    arm.open()


    # arm.disable_all()

    print arm.dyn_chain.get_motor_list(broadcast=False)


    # print arm.get_position()


    arm.close()

if __name__ == '__main__':
    main_test_crochets()
    pass
