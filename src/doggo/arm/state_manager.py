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


class StateManager(Thread):
    def __init__(self, keys, gpio):
        '''
        keys :: dict(string => int) # Keys currently pressed
        '''
        Thread.__init__(self)
        self.keys = keys
        self.gpio = gpio
        self.running = True
        self.current_state = None
        self.stop_event = Event()

    def stop(self):
        self.current_state = None

    def run(self):
        while self.running:
            try:
                if self.current_state:
                    self.current_state.update(self)

                self.sleep(0.01)

            except StateStop:
                if self.current_state:
                    self.current_state.stop()

                self.current_state = None
                self.stop_event.clear()

    def sleep(self, sleep_time):
        time_elapsed = 0

        while time_elapsed < sleep_time:
            if self.stop_event.is_set():
                raise StateStop()

            time_elapsed += 0.01
            time.sleep(0.01)

    def set_state(self, state):
        self.stop_event.clear()
        self.current_state = state


class ArmStateManager(StateManager):
    def __init__(self, arm, keys, gpio):
        StateManager.__init__(self, keys, gpio)

        self.arm = arm

    def stop(self):
        self.arm.stop_movement()
        self.current_state = None

    def wait_stopped(self):
        self.arm.wait_stopped_sleep(self.sleep)


class State:
    def __init__(self):
        self.state_manager = None

    def update(self):
        pass

    def stop(self):
        pass


class ArmManuelState(State):
    def __init__(self):
        State.__init__(self)
        self.current_position = [0, 200, 200, 0]

    def update(self):
        if 't' in self.state_manager.keys:
            new_position = self.current_position[:]
            new_position[2] += 20
            self.write_goal(new_position)

    def write_goal(self, position):
        if self.current_position != position:
            self.current_position = position

            self.state_manager.arm.goto(position)

            self.state_manager.wait_stopped()


class ArmPickupState(State):
    def update(self, state_manager):
        # simba
        state_manager.arm.write_goal_without_base(225, 483, 191, speed=150)
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
