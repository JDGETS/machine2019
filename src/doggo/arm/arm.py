from ik import ik
from dxl.dxlchain import DxlChain
from collections import namedtuple
import math
import time

USB_PORT = '/dev/ttyUSB0'

Point = namedtuple('Point', ['x', 'y', 'z', 'r'])


def map_to(value, istart, istop, ostart, ostop):
    return 1.0*ostart + (1.0*ostop - 1.0*ostart) * ((1.0*value - 1.0*istart) / (1.0*istop - 1.0*istart))

class Arm:
    def __init__(self, port=USB_PORT):
        self.port = port
        self.goal = Point(0, 0, 0, 0)
        self.opened = False


    def open(self):
        self.dyn_chain = DxlChain(self.port, rate=1000000)
        self.dyn_chain.open()

        self.motors = self.dyn_chain.get_motor_list()

        assert len(self.motors) == 5, 'Some arm motors are missing. Expected 5 instead got %d' % len(self.motors)

        self.opened = True

    def close(self):
        self.opened = False
        self.dyn_chain.close()

    def goto(self, x, y, z, r):
        self.goal = Point(x, y, z, r)

        joints = ik(*self.goal)
        joints = map(math.degrees, joints)
        goals = self.angles_to_motors(*joints)

        return self.write_goal(*goals)

    def write_23(self, pos, pos4, pos5, speed=100):
        self.dyn_chain.sync_write_pos_speed([2, 3, 4, 5], [pos, 1023 - pos, pos4, pos5], [speed]*4)

    def write_goal(self, goal1, goal23, goal4, goal5, speed=50):
        '''
        Write goal positions of all servos with given speed
        '''
        self.dyn_chain.sync_write_pos_speed([1, 2, 3, 4, 5], [goal1, goal23, 1023 - goal23, goal4, goal5], [speed]*4)

    def angles_to_motors(self, a1, a23, a4, a5):
        '''
        Converts angles to motor goal positions
        '''
        goal1 = map_to(a1, 0, 90, 826, 521)
        goal23 = map_to(180 - a23, 10, 180, 227, 820)
        goal4 = map_to(a4, 0, 180, 804, 192)
        goal5 = map_to(a5, 90, -90, 213, 805)

        return (goal1, goal23, goal4, goal5)

    def motors_to_angles(self, goal1, goal23, goal4, goal5):
        '''
        Converts motor goal positions to angles
        '''
        a1 = map_to(goal1, 0, 100, -90, 90)
        a23 = 180 - map_to(goal23, 227, 820, 10, 180)
        a4 = map_to(goal4, 804, 192, 0, 180)
        a5 = map_to(goal5, 213, 805, 90, -90)

        return (a1, a23, a4, a5)


if __name__ == '__main__':
    arm = Arm()

    # arm.open()
    # arm.dyn_chain.goto(5, 512, 100)
    print arm.goto(200, 0, 300, 0)
    print arm.goto(0, 200, 300, 0)
    print arm.goto(0, -200, 300, 0)
