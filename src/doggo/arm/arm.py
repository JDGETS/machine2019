from ik import ik
from dxl.dxlchain import DxlChain
from collections import namedtuple
import math
import time
import rpyc

USB_PORT = '/dev/ttyUSB0'

Point = namedtuple('Point', ['x', 'y', 'z', 'r'])


def map_to(value, istart, istop, ostart, ostop):
    return 1.0*ostart + (1.0*ostop - 1.0*ostart) * ((1.0*value - 1.0*istart) / (1.0*istop - 1.0*istart))


def motors_to_angles(self, goal1, goal23, goal4, goal5):
    '''
    Converts motor positions to angles
    '''
    a1 = map_to(goal1, 826, 521, 0, 90)
    a23 = 180 - map_to(goal23, 227, 820, 10, 180)
    a4 = map_to(goal4, 804, 192, 0, 180)
    a5 = map_to(goal5, 213, 805, 90, -90)

    return (a1, a23, a4, a5)


def angles_to_motors(self, a1, a23, a4, a5):
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

    def open(self):
        self.dyn_chain = DxlChain(self.port, rate=1000000)
        self.dyn_chain.open()

        self.motors = self.dyn_chain.get_gmotor_list()

        assert len(self.motors) == 5, 'Some arm motors are missing. Expected 5 instead got %d' % len(self.motors)

        self.opened = True

    def close(self):
        self.opened = False
        self.dyn_chain.close()

    def goto(self, x, y, z, r, speed=50):
        '''
        Uses inverse kinematic to go to a position in space

        '''
        self.goal = Point(x, y, z, r)

        joints = ik(*self.goal)
        joints = map(math.degrees, joints)
        goals = angles_to_motors(*joints)

        return self.write_goal(*goals, speed=speed)

    def write_goal(self, goal1, goal23, goal4, goal5, speed=50):
        '''
        Write goal positions of all servos with given speed
        '''
        self.dyn_chain.sync_write_pos_speed([1, 2, 3, 4, 5], [goal1, goal23, 1023 - goal23, goal4, goal5], [speed]*5)

    def disable_all(self):
        '''
        Disable torque of all motors
        '''
        self.dyn_chain.disable()


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

    def move_get_crochet(self):
        pre_crochet = (602, 435, 767, 378)
        get_crochet = (608, 534, 771, 463)
        post_crochet = (602, 435, 767, 378)
        figurine = (813, 709, 522, 440)
        tyro = (190, 415, 624, 257)

        self.write_goal(*pre_crochet, speed=75)

        self.dyn_chain.wait_stopped()

        self.write_goal(*get_crochet)

        self.dyn_chain.wait_stopped()

        time.sleep(1)

        self.write_goal(*post_crochet, speed=50)

        self.dyn_chain.wait_stopped()

        self.write_goal(*figurine, speed=50)

        self.dyn_chain.wait_stopped()

        self.write_goal(*tyro, speed=50)

        self.dyn_chain.wait_stopped()


# RPC service to have access to the arm remotely
class ArmService(rpyc.Service):

    def __init__(self):
        self.arm = Arm()

    def on_connect(self, conn):
        # code that runs when a connection is created
        # (to init the service, if needed)
        self.arm.open()

    def on_disconnect(self, conn):
        # code that runs after the connection has already closed
        # (to finalize the service, if needed)
        self.arm.close()

    # this is an exposed method
    def exposed_move_to_pos(self, pose):

        x = pose['x']
        y = pose['y']
        z = pose['z']
        r = pose['r']

        self.arm.goto(x, y, z, r)

    def exposed_get_question(self):  # while this method is not exposed
        return "what is the airspeed velocity of an unladen swallow?"


def main_test_crochets():

    arm = Arm()
    arm.open()

    arm.move_get_crochet()

    arm.disable_all()

    print arm.get_position()

    print arm.dyn_chain.get_reg(4, "present_load") & 1023
    print arm.motors_load()

    arm.close()
    print arm.motors_load()


def main_test_rpc():
    from rpyc.utils.server import ThreadedServer
    RPC_PORT = 18861
    t = ThreadedServer(ArmService, port=RPC_PORT)
    t.start()


if __name__ == '__main__':
    #main_test_crochets()
    #main_test_rpc()
