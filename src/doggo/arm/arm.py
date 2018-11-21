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

        return map(math.degrees, joints)

    def write_23(self, pos, pos4, pos5, speed=100):
        self.dyn_chain.sync_write_pos_speed([2, 3, 4, 5], [pos, 1023 - pos, pos4, pos5], [speed]*4)


if __name__ == '__main__':
    arm = Arm()

    arm.open()

    points = [(300, 0, 100, math.radians(-45)),
              (200, 0, 100, math.radians(-45)),
              (200, 0, 0, math.radians(-45)),
              (300, 0, 0, math.radians(-45))]

    # arm.dyn_chain.goto(5, 512, 100)

    for p in points:
        joints = arm.goto(*p)
        print joints
        a4 = map_to(joints[2], 0, 180, 804, 192)
        a23 = map_to(180 - joints[1], 10, 180, 227, 820)

        a5 = map_to(joints[3], 90, -90, 213, 805)

        arm.write_23(a23, a4, a5)

        print a5

        time.sleep(1.5)

    # arm.dyn_chain.disable([2,3,4])

    arm.close()
