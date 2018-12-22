from threading import Thread, Event
import time


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
    def __init__(self, keys):
        '''
        keys :: dict(string => int) # Keys currently pressed
        '''
        Thread.__init__(self)
        self.keys = keys
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
    def __init__(self, arm, keys):
        StateManager.__init__(self, keys)

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
        state_manager.arm.write_goal_without_base(225, 483, 191)
        state_manager.wait_stopped()

        # rotate base
        state_manager.arm.write_single_goal(1, 573)
        state_manager.wait_stopped()

        # place le bonhomme
        state_manager.arm.write_goal(558, 422, 567, 196)
        state_manager.wait_stopped()

        # rotate a bit
        state_manager.arm.write_single_goal(1, 507)
        state_manager.wait_stopped()

        # switch to manual
        state_manager.stop()
