#!/usr/bin/python

from dxl.dxlchain import DxlChain
from dxl.dxlcore import DxlCommunicationException
from Servo import Servo
from MachineIK import MachineIK
import time
import math as m
from collections import OrderedDict
import curses
import os
import shutil
import json

class GPIOStub:
    HIGH = 1
    LOW = 0
    BOARD = 0
    OUT = 1

    def __init__(*args):
        pass

    def output(*args):
        pass

    def input(*args):
        pass

    def setup(*args):
        pass

    def setmode(*args):
        pass

GPIO = GPIOStub()

# from Core.MachineModule import AdafruitPCA9685ModuleConstants
# from Core.MachineNetwork import Localhost

DYN_CTRL = 40
USB_PORT = "/dev/ttyUSB0"


class ArmCtrl(object):
    def __init__(self, a):
        # Open the serial device
        self.dyn_chain = a
        self.servos = Servo()
        self.mik = MachineIK()

        # self.labeler = Labeler()

        self.INIT_TEST = False
        self.VIEW_POS_RT = False
        self.curr_joints = [p for key, p in self.dyn_chain.get_position([1, 2, 4, 6]).items()]
        self.curr_pos = self.get_arm_pose()

    def _restart_dyn(self):
        GPIO.output(DYN_CTRL, GPIO.HIGH)
        time.sleep(1.0)
        GPIO.output(DYN_CTRL, GPIO.LOW)

    def _int2rad(self, pos, offset=False, degrees=False):
        int_offset = 1023 if offset is True else 0
        step = 0.29 if degrees is True else 0.005061455
        dyn_offset = 30 if degrees is True else m.pi / 6
        return [(int_offset - v) * step + dyn_offset for v in pos]

    def _rad2int(self, pos, offset=True, degrees=False):
        int_offset = 1023 if offset is True else 0
        step = 0.29 if degrees is True else 0.005061455
        dyn_offset = 30 if degrees is True else m.pi / 6
        return [int(int_offset - (v - dyn_offset) / step) for v in pos]

    def write_json(self, message):
        j_mess = json.dumps(dict(message))
        print j_mess
        mess = self.read_json(j_mess)
        print mess
        return j_mess

    def read_json(self, j_mess):
        return json.loads(j_mess)

    def home_pos(self):
        self.curr_joints = self.dyn_chain.get_position([1, 2, 4, 6])
        home = self.dyn_chain.load_position('positions/home.position')
        max_speed = self.mik.get_spd_joint([self.curr_joints[1], self.curr_joints[2], self.curr_joints[4], self.curr_joints[6]],
                                          [home[1], home[2], home[3], home[4]], 50)

        # Realize motion to new pos
        self.dyn_chain.enable()
        self.dyn_chain.goto(1, home[1], speed=max_speed[0], blocking=False)
        self.dyn_chain.sync_write_pos_speed([2, 3], [home[2], 1023 - home[2]],
                                            speeds=[max_speed[1]] * 2)
        self.dyn_chain.sync_write_pos_speed([4, 5], [home[3], 1023 - home[3]],
                                            speeds=[max_speed[2]] * 2)
        self.dyn_chain.goto(6, home[4], speed=max_speed[3], blocking=False)
        while self.dyn_chain.is_moving():
            print self.dyn_chain.get_position([1, 2, 4, 6])
        # Record new current position
        self.curr_joints = self.dyn_chain.get_position([1, 2, 4, 6])

    def init_pos(self):
        if self.INIT_TEST:
            # Get to home for testing phase
            print '========ARM TEST SEQUENCE'
            print 'Going to home position'
            self.home_pos()
            time.sleep(1)
            print 'Test getting flag 1 and 2 in loader'
            self.execute_motion('get12')
            time.sleep(1)
            print 'Test rebooting dynamixels'
            self._restart_dyn()
            time.sleep(1)
            print 'Going to home position'
            self.home_pos()
            time.sleep(1)
            print 'Test storing flag 1 and 2 in loader'
            self.execute_motion('put12')
            time.sleep(1)
            print 'Test IR and MOTOR of labeler'
            time.sleep(1)
            #self.labeler.cycle()
            time.sleep(1)
            print 'Test gripper IR, put and remove object in front of it'
            start_time = time.time()
            while (time.time() - start_time) < 10:
                #self.labeler.read_ir_label()
                pass
        # Move to home position
        self.home_pos()

    def execute_motion(self, name):
        function_dict = {'cycle_labeler': self.labeler.cycle, 'sleep': time.sleep(1), 'set_dist_sonar': self.set_dist_sonar}

        try:
            motion = json.load(open('motions/' + name))

            # Parse the sequence of arm's poses and states
            for key in range(len(motion)):
                # Get the next pose to go
                pose = [float(p) for p in motion[str(key + 1)]["pose"]]
                # Get the state to assign to gripper
                grip_r = motion[str(key + 1)]["grippers"]["right"]
                grip_l = motion[str(key + 1)]["grippers"]["left"]
                torque = motion[str(key + 1)]["grippers"]["torque"]
                function_name = motion[str(key + 1)]["function"]
                if len(function_name):
                    function_dict[function_name]()
                # Update servo state
                self.servos.R_GRP_ST = grip_r
                self.servos.L_GRP_ST = grip_l
                self.servos.TORQUE = torque
                # Update robot state
                try:
                    if function_name != "set_dist_sonar":
                        self.send2pose(pose)
                        self.servos.update()
                except DxlCommunicationException as e:
                    self._restart_dyn()
                    self.send2pose([float(p) for p in motion[str(key-1)]["pose"]])
                    print 'Couldnt execute movement, going back to home'
                    self.home_pos()
                    break

        except IOError as e:
            print 'Motion name not available'

        if name != "getLeft":
            self.home_pos()

    def motion_replay(self):
        print '==============Enter name of motion to replay:'
        name = raw_input()
        motion = OrderedDict()

        function_dict = {'cycle_labeler': self.labeler.cycle}

        try:
            motion = json.load(open('motions/' + name))
            # Parse the sequence of arm's poses and states
            for key in range(len(motion)):
                # Get the next pose to go
                pose = [float(p) for p in motion[str(key + 1)]["pose"]]
                # Get the state to assign to grippers
                grip_r = motion[str(key + 1)]["grippers"]["right"]
                grip_l = motion[str(key + 1)]["grippers"]["left"]
                torque = motion[str(key + 1)]["grippers"]["torque"]
                function_name = motion[str(key + 1)]["function"]
                if len(function_name):
                    function_dict[function_name]()
                # Update servo state
                self.servos.R_GRP_ST = grip_r
                self.servos.L_GRP_ST = grip_l
                self.servos.TORQUE = torque
                # Update robot state
                try:
                    self.send2pose(pose)
                    self.servos.update()
                except DxlCommunicationException as e:
                    self._restart_dyn()
                    self.send2pose([float(p) for p in motion[str(key-1)]["pose"]])
                    print 'Couldnt execute movement, going back to home'
                    self.home_pos()
                    break


        except IOError as e:
            print 'Motion name not available'

        if str(name) != "getLeft":
            if str(name) != "getRight":
                self.home_pos()

    def send2pose(self, goal, speed_lim=85, blocking=True):
        self.curr_joints = [p for key, p in self.dyn_chain.get_position([1, 2, 4, 6]).items()]
        # Compute joints position with IK and constant speed
        matrix = self.mik.pos_to_dh(goal)
        new_joints_model = self.mik.inverse_kinematics(matrix)
        new_joints_motor = self._rad2int(self.mik.chain_to_motor(new_joints_model), offset=True)
        # new_joints_motor[3] -= 25  # Angle offset for gripper
        max_speed = self.mik.get_spd_joint(self.curr_joints, new_joints_motor, speed_lim)

        # Realize motion to new pos
        self.dyn_chain.enable()
        self.dyn_chain.goto(1, new_joints_motor[0], speed=max_speed[0], blocking=False)
        self.dyn_chain.sync_write_pos_speed([2, 3], [new_joints_motor[1], 1023 - new_joints_motor[1]],
                                            speeds=[max_speed[1]] * 2)
        self.dyn_chain.sync_write_pos_speed([4, 5], [new_joints_motor[2], 1023 - new_joints_motor[2]],
                                            speeds=[max_speed[2]] * 2)
        self.dyn_chain.goto(6, new_joints_motor[3], speed=max_speed[3], blocking=False)
        if blocking:
            while self.dyn_chain.is_moving():
                print self.dyn_chain.get_position([1, 2, 4, 6])

    def send2poselin(self, goal):
        self.curr_joints = [p for key, p in self.dyn_chain.get_position([1, 2, 4, 6]).items()]
        # Compute joints position with IK and constant speed
        matrix = self.mik.pos_to_dh(goal)
        new_joints_model = self.mik.inverse_kinematics(matrix)
        new_joints_motor = self._rad2int(self.mik.chain_to_motor(new_joints_model), offset=True)
        # new_joints_motor[3] -= 25  # Angle offset for gripper
        curr_pos = self.get_arm_pose()
        max_speed = self.mik.get_spd_lin(curr_pos, goal, 10000)
        # Realize motion to new pos
        self.dyn_chain.enable()
        self.dyn_chain.goto(1, new_joints_motor[0], speed=max_speed[0], blocking=False)
        self.dyn_chain.goto(2, new_joints_motor[1], speed=max_speed[1], blocking=False)
        self.dyn_chain.goto(3, 1023 - new_joints_motor[1], speed=max_speed[1], blocking=False)
        self.dyn_chain.goto(4, new_joints_motor[2], speed=max_speed[2], blocking=False)
        self.dyn_chain.goto(5, 1023 - new_joints_motor[2], speed=max_speed[2], blocking=False)
        self.dyn_chain.goto(6, new_joints_motor[3], speed=max_speed[3], blocking=False)
        while self.dyn_chain.is_moving():
            print self.dyn_chain.get_position([1, 2, 4, 6])

    def get_arm_pose(self):
        self.curr_joints = [p for key, p in self.dyn_chain.get_position([1, 2, 4, 6]).items()]
        radmotors = self._int2rad(self.curr_joints, offset=True)
        radchain = self.mik.motor_to_chain(radmotors)
        rot_matrix = self.mik.direct_kinematics(radchain)
        self.curr_pos = self.mik.dh_to_pos(rot_matrix)
        return [self.curr_pos[0], self.curr_pos[1], self.curr_pos[2], 0, 0, 0]


if __name__ == "__main__":
    # Power cycle dynamixels
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(DYN_CTRL, GPIO.OUT)
    GPIO.output(DYN_CTRL, GPIO.HIGH)
    time.sleep(0.1)
    GPIO.output(DYN_CTRL, GPIO.LOW)
    dyn_chain = DxlChain(USB_PORT, rate=1000000)
    # Load all the motors and obtain the list of IDs
    motors = dyn_chain.get_motor_list()  # Discover all motors on the chain and return their IDs

    print motors

    act_pos = dyn_chain.get_position()
    arm = ArmCtrl(dyn_chain)
    arm.curr_joints = dyn_chain.get_position([1, 2, 4, 6])
    arm.init_pos()
    # Disable the motors
    if arm.VIEW_POS_RT:
        while True:
            joints = arm._int2rad(arm.curr_joints, offset=True)
            print joints
            time.sleep(0.5)

    print "===============Enter a command"
    while True:
        i = raw_input()

        if i == "p":
            print 'Enter [x, y, z, r, p, y] position'  # test = -100, -100, 200, 0, 1.5708, 0
            pose = [float(p) for p in raw_input().split(',')]
            arm.send2pose(pose)
            print "===============Going to pose 1"
            print "===============Pose achieved, enter next command..."
        elif i == "k":
            print dyn_chain.get_position([1, 2, 4, 6])
        elif i == "l":
            print 'Enter [x, y, z, r, p, y] position to as lin from current position'  # test = -290, 100, -80, 0, 0, 0
            pose = [float(p) for p in raw_input().split(',')]
            arm.send2poselin(pose)
            print "===============Going to pose 1"
            print "===============Pose achieved, enter next command..."
        elif i == "b":
            print "Move base :"
            pos = raw_input()
            print arm.dyn_chain.goto(1, int(pos), speed=50, blocking=False)
        elif i == "d":
            print "===============Disabled"
            arm.dyn_chain.disable()
        elif i == "e":
            print "===============Enabled"
            arm.dyn_chain.enable()
        elif i == "r":
            arm.motion_replay()
            print "Motion done..."
        elif i == "1":
            print 'Switching right grip'
            arm.servos.R_GRP_ST = True if arm.servos.R_GRP_ST == False else False
            arm.servos.update()
        elif i == "2":
            print 'Switching left grip'
            arm.servos.L_GRP_ST = True if arm.servos.L_GRP_ST == False else False
            arm.servos.update()
        elif i == "t":
            arm.servos.TORQUE = True if arm.servos.TORQUE == False else False
            if arm.servos.TORQUE:
                print 'Torque engaged'
            else:
                print 'Torque disengaged'
        elif i == "g":
            print 'Reboot dynamixels'
            arm._restart_dyn()
            print 'Done'

        elif i == "c":
            print 'Cycling labeler'
            arm.labeler.cycle()
            print 'Done'
