from threading import Thread, Event
import time
import config


class StateStop(Exception):
    pass

class KeyBouncer:
    def __init__(self, keys, target_key):
        self.keys = keys
        self.target_key = target_key
        self.flag = False

    def is_pressed(self):
        if self.target_key in self.keys and not self.flag:
            self.flag = True

        if self.target_key not in self.keys:
            self.flag = False


class ArmStateManager(Thread):
    def __init__(self, arm, keys, gpio):
        Thread.__init__(self)

        self.keys = keys
        self.gpio = gpio
        self.running = True
        self.current_state = None
        self.stop_event = Event()
        self.set_state(ArmManuelState())
        self.arm = arm

    def set_state(self, state):
        self.stop_event.clear()
        print 'set state = ' + str(state)
        self.current_state = state

    def sleep(self, sleep_time):
        # print 'sleep'

        time_elapsed = 0

        while time_elapsed < sleep_time:
            if self.stop_event.is_set():
                raise StateStop()

            time_elapsed += 0.01
            time.sleep(0.01)


    def run(self):
        while self.running:
            try:
                if not self.current_state:
                    self.current_state = ArmManuelState()
                    self.stop_event.clear()

                self.current_state.update(self)

                self.sleep(0.01)

            except:
                print 'STATE STOP'
                if self.current_state:
                    self.current_state.stop()

                self.current_state = None
                self.stop_event.clear()

    def stop(self):
        print 'stop state = ' + str(self.current_state)

        self.stop_event.set()
        self.arm.stop_movement()
        self.current_state = None

    def wait_stopped(self):
        print 'wait_stopped'
        self.arm.wait_stopped_sleep(self.sleep)


class State:
    def __init__(self):
        self.state_manager = None

    def update(self):
        pass

    def stop(self):
        pass


class ArmManuelState(State):
    ARM_STEP = 10
    ARM_WRIST_STEP = 5
    HOME = [85, 230, -18]

    def __init__(self):
        State.__init__(self)
        self.state_manager = None
        self.base_direction = 0
        self.position_2d = self.HOME
        self.frame = 0
        self.last_update = -10


    def update(self, state_manager):
        self.state_manager = state_manager

        keys = state_manager.keys
        ay, az, ar = self.position_2d

        if 'o' in keys:
            self.set_base_direction(1)
        elif 'i' in keys:
            self.set_base_direction(-1)
        else:
            self.set_base_direction(0)


        if self.frame - self.last_update > 0:
            if 't' in keys:
                ay += self.ARM_STEP
            elif 'g' in keys:
                ay -= self.ARM_STEP

            if 'y' in keys:
                az += self.ARM_STEP
            elif 'h' in keys:
                az -= self.ARM_STEP

            if 'u' in keys:
                ar += self.ARM_WRIST_STEP
            elif 'j' in keys:
                ar -= self.ARM_WRIST_STEP

            self.write_2d([ay, az, ar])

        self.frame += 1

        self.state_manager.sleep(0.02)

    def write_2d(self, pos):
        if self.position_2d != pos:
            self.position_2d = pos
            print 'arm = ' + str(pos)
            self.last_update = self.frame

            self.state_manager.arm.goto2D(pos[0], pos[1], pos[2], speed=100)

    def set_base_direction(self, direction):
        if self.base_direction != direction:
            self.state_manager.arm.move_base(direction, speed=100)
            self.base_direction = direction

            # ask to stop base move
            if direction == 0:
                # get current position?
                pass

    def set_position(self, pos):
        pass


class ArmFirstHuman(State):
    # just to note pos of arm for saving first dude
    arm = [315, -70, -318]


class ArmHomeState(State):
    def update(self, state_manager):

        # home
        state_manager.arm.goto2D(85, 230, -18, speed=150)
        state_manager.wait_stopped()

        state_manager.arm.stop()


class ArmPickupState(State):
    def update(self, state_manager):
        # simba
        state_manager.arm.write_goal_without_base(225, 483, 191, speed=100)
        state_manager.wait_stopped()

        # rotate base
        state_manager.arm.write_single_goal(1, 616, speed=250)
        state_manager.wait_stopped()

        # place le bonhomme
        state_manager.arm.write_goal(616, 421, 560, 198, speed=100)
        state_manager.wait_stopped()

        # rotate a bit
        state_manager.arm.write_single_goal(1, 495, speed=150)
        state_manager.wait_stopped()

        # switch to manual
        state_manager.stop()


class ArmReleaseState(State):
    def update(self, state_manager):
        state_manager.gpio.set_servo_pulsewidth(config.doggo_servo_arm_grip_channel, 1500)
        time.sleep(0.5)
        state_manager.gpio.set_servo_pulsewidth(config.doggo_servo_arm_grip_channel, 0)

        state_manager.arm.write_single_goal(2, 283, speed=100)

        state_manager.wait_stopped()

        state_manager.stop()


class PickupCrochetState(State):
    def __init__(self, number):
        State.__init__(self)
        self.number = number
        self.crochets = {
            1: [(928, 433, 768, 433), (928, 478, 777, 451)],
            2: [(871, 412, 784, 424), (871, 460, 794, 461)]
        }

    def update(self, state_manager):
        state_manager.gpio.set_servo_pulsewidth(config.doggo_servo_arm_grip_channel, 1500)
        time.sleep(0.5)
        state_manager.gpio.set_servo_pulsewidth(config.doggo_servo_arm_grip_channel, 0)

        before, target = self.crochets[self.number]

        # home
        state_manager.arm.goto2D(85, 200, -18, speed=150)
        state_manager.wait_stopped()

        state_manager.arm.write_single_goal(1, before[0], speed=250)
        state_manager.wait_stopped()

        state_manager.arm.write_goal(*before)
        state_manager.wait_stopped()

        state_manager.arm.write_goal(*target)
        state_manager.wait_stopped()

        state_manager.gpio.set_servo_pulsewidth(config.doggo_servo_arm_grip_channel, 1200)
        time.sleep(0.5)
        state_manager.gpio.set_servo_pulsewidth(config.doggo_servo_arm_grip_channel, 0)

        state_manager.arm.write_goal(*before)
        state_manager.wait_stopped()

        state_manager.stop()


class TestState(State):
    def __init__(self):
        State.__init__(self)

        self.flag = True

    def update(self, state_manager):

        for i in range(10):
            print state_manager.stop_event.is_set()

            self.flag = not self.flag
            if self.flag:
                state_manager.arm.goto2D(85, 200, -18, speed=150)
            else:
                state_manager.arm.goto2D(230, 120, 0, speed=150)

            state_manager.wait_stopped()
