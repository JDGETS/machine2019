# import Adafruit_PCA9685 as pca


class Servo:
    def __init__(self):
        # self.pwm = pca.PCA9685()
        # self.pwm.set_pwm_freq(100)
        self.RIGHT_GRIP = 4
        self.LEFT_GRIP = 5
        self.R_GRP_ST = False
        self.L_GRP_ST = False
        self.TORQUE = False
        self.update()

    def gripper_state(self, gripper, closed=False):
        '''
        if closed:
            self.pwm.set_pwm(gripper, 0, 300)
            if self.TORQUE:
                self.pwm.set_pwm(gripper, 0, 205)
        else:
            self.pwm.set_pwm(gripper, 0, 750)
        '''

    def update(self):
        '''
        self.gripper_state(self.RIGHT_GRIP, self.R_GRP_ST)
        self.gripper_state(self.LEFT_GRIP, self.L_GRP_ST)
        '''
