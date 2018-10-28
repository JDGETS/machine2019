from Core.MachineModule import MachineModule, ArmModuleConstants, ControlModuleConstants
from ArmCtrl import ArmCtrl
from Core.MachineNetwork import Localhost
from dxl.dxlchain import DxlChain
import time
from Control.seq_functions.Messages import ARM_MODE_SPACE, ARM_MODE_RIGHT, ARM_MODE_MOON,ARM_MODE_LEFT ,ARM_MODE_BASE,ARM_MODE_DESERT
import sys
import traceback
import json
import RPi.GPIO as GPIO

USB_PORT = "/dev/dynamixel"
DYN_CTRL = 40

class ArmState(object):

    def __init__(self):
        self.joints = 0
        self.current_pos = 0
        self.leftGrip = 0
        self.rightGrip = 0
        self.torque = 0
        self.gripIr = 0
        self.labelIr = 0

    def __iter__(self):
        try:
            yield('joints', self.joints)
            yield('current_pos', self.current_pos)
            yield('leftGrip', self.leftGrip)
            yield('rightGrip', self.rightGrip)
            yield('torque', self.torque)
            yield('gripIr', self.gripIr)
            yield('labelIr', self.labelIr)

        except Exception as e:
            print e


class ArmModule(MachineModule):
    def __init__(self, topic):
        super(ArmModule, self).__init__(topic)
        self.model_current_pos = None
        self.arm = None
        self.xyz_model = [0, 0, 0, 0, 0, 0]
        self.xyz_velocity = [0.0, 0.0, 0.0]

    def start(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(DYN_CTRL, GPIO.OUT)
        GPIO.output(DYN_CTRL, GPIO.HIGH)
        time.sleep(1.0)
        GPIO.output(DYN_CTRL, GPIO.LOW)
        dyn_chain = DxlChain(USB_PORT, rate=1000000)
        print 'Started'
        motors = dyn_chain.get_motor_list()  # Discover all motors on the chain and return their IDs
        act_pos = dyn_chain.get_position()

        self.arm = ArmCtrl(dyn_chain)
        self.model_current_pos = self.arm.get_arm_pose()
        self.arm.init_pos()
        self.send_arm_state()

        self.xyz_model[0] = self.arm.get_arm_pose()[0]
        self.xyz_model[1] = self.arm.get_arm_pose()[1]
        self.xyz_model[2] = self.arm.get_arm_pose()[2]

        super(ArmModule, self).start()

    def loop(self):
        armState = ArmState()

        #
        # COMMAND RECU PAR LE MODULE ARM VIA AUTOMATION
        #   Socle detecter a gauche; Socle detecter a droite
        #
        #
        #
        #   Le bras doit faire les mouvements ou le robot doit regarder
        #
        #
        #   UNE MIRE AU MILIEU POUR LES SOCLES, UNE MIRE POUR LES BATTONS DOUBLES
        #
        #

        while self.is_running():
            new_zero_velocity = False
            msgs = self.pop_messages()
            for msg in msgs:
                msg = msg['message']
                if 'action' in msg:
                    if msg['action'] == 'move_to':
                        x, y, z = msg['xyz']
                        # changer la coordonnes avec la valeur donner
                    elif msg['action'] == 'rotate_to':
                        # faire tourner la camera a un point precis
                        pass
                    elif msg['action'] == 'left_toggle':
                        # faire tourner la camera a un point precis
                        self.arm.servos.L_GRP_ST = not self.arm.servos.L_GRP_ST
                        self.arm.servos.update()
                    elif msg['action'] == 'right_toggle':
                        # faire tourner la camera a un point precis
                        self.arm.servos.R_GRP_ST = not self.arm.servos.R_GRP_ST
                        self.arm.servos.update()

                    elif 'sequence' in msg['action']:
                        if msg['action']['sequence'] == 'seq_tab':
                            sequence_to_launch = 'get'+str(raw_input())
                            print sequence_to_launch
                            self.arm.execute_motion(sequence_to_launch)

                elif 'event' in msg:
                    if msg['event'] == 'socle_a_droite':
                        d = msg['dist']

                        pass
                    elif msg['event'] == 'socle_a_gauche':
                        d = msg['dist']
                        pass
                elif 'mode' in msg:
                    if msg['mode'] == ARM_MODE_BASE:
                        pass
                    elif msg['mode'] == ARM_MODE_DESERT:
                        pass
                    elif msg['mode'] == ARM_MODE_MOON:
                        pass
                    elif msg['mode'] == ARM_MODE_LEFT:
                        pass
                    elif msg['mode'] == ARM_MODE_RIGHT:
                        pass
                    elif msg['mode'] == ARM_MODE_SPACE:
                        pass
                elif 'manual_move' in msg:
                    # SUBSCRIBE GOAL POS FROM CONTROL MODULE
                    pose = msg['manual_move']['pose']
                    self.xyz_velocity[0] = pose[0]
                    self.xyz_velocity[1] = pose[1]
                    self.xyz_velocity[2] = pose[2]

                    if pose == [0.0, 0.0, 0.0]:
                        new_zero_velocity = True

                    #self.model_current_pos[0] += pose[0]
                    #self.model_current_pos[1] += pose[1]
                    #self.model_current_pos[2] += pose[2]
                    # speed = msg['manual_move']['speed']
                    #speed = 50
                    #print self.model_current_pos
                    # self.send_arm_state()
                    # print self.xyz_velocity

            if self.xyz_velocity != [0.0, 0.0, 0.0] or new_zero_velocity:

                model_update_speed = 5
                arm_mvt_speed = 50
                if new_zero_velocity:
                    new_zero_velocity = False
                self.xyz_model[0] += self.xyz_velocity[0] * model_update_speed
                self.xyz_model[1] += self.xyz_velocity[1] * model_update_speed
                self.xyz_model[2] += self.xyz_velocity[2] * model_update_speed

                new_abs_pos = [int(round(p)) for p in self.xyz_model]
                print new_abs_pos

                self.arm.send2pose(new_abs_pos, speed_lim=arm_mvt_speed, blocking=False)

            time.sleep(0.1)

    def send_arm_state(self):
        # Read arm inputs and send back to control module
        self.model_current_pos = self.arm.get_arm_pose()

        armState = ArmState()

        armState.joints = self.arm.curr_joints
        armState.current_pos = self.model_current_pos
        armState.leftGrip = self.arm.servos.L_GRP_ST
        armState.rightGrip = self.arm.servos.R_GRP_ST
        armState.torque = self.arm.servos.TORQUE
        armState.gripIr = self.arm.labeler.read_ir_grasper()
        armState.labelIr = self.arm.labeler.read_ir_label()

        msg = dict(armState)
        # self.send_message(Localhost, ControlModuleConstants, {'ArmState': msg})
        msg = {
            "ArmState": {"Arm": {"Joints": self.arm.curr_joints, "Pose": self.model_current_pos}}}#,
                         # "Grippers": {"LeftGrip": 0}}}#,self.arm.servos.L_GRP_ST
                         #              'RightGrip': self.arm.servos.R_GRP_ST,
                         #              'Torque': self.arm.servos.TORQUE,
                         #              'GripIR': self.arm.labeler.read_ir_grasper()},
                         # 'Labeler': {'LabelIR': self.arm.labeler.read_ir_label()}}}
        #print msg
        self.send_message(Localhost, ControlModuleConstants, dict(msg))


if __name__ == '__main__':
    m = None
    try:
        m = ArmModule(ArmModuleConstants)
        m.start()

    except Exception as e:
        traceback.print_exc(file=sys.stderr)

    finally:
        m.stop()
