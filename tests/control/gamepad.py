from inputs import get_gamepad
from tests.control.motion_control import MotionController
import inputs

pressed = 1
released = 0

# Control modes
wheels = "traction1"


class DictManette(object):

    def __init__(self):
        self.y = 0
        self.x = 0
        self.b = 0
        self.a = 0
        self.rb = 0
        self.lb = 0
        self.rt = 0
        self.lt = 0
        self.start = 0
        self.back = 0
        self.padVertical  = 0
        self.padHorizontal = 0
        self.rightJoyX = 0
        self.rightJoyY = 0
        self.leftJoyY = 0
        self.leftJoyX = 0
        self.leftTrigger = 0
        self.rightTrigger = 0
        self.centralButton = 0

    def __iter__(self):
        try:
            yield('x', self.x)
            yield('y', self.y)
            yield('b', self.b)
            yield('a', self.a)
            yield('rb', self.rb)
            yield('lb', self.lb)
            yield('rt', self.rt)
            yield('lt', self.lt)
            yield('start', self.start)
            yield('back', self.back)
            yield('padHorizontal', self.padHorizontal)
            yield('padVertical', self.padVertical)
            yield('rightJoyX', self.rightJoyX)
            yield('rightJoyY', self.rightJoyY)
            yield('leftJoyX', self.leftJoyX)
            yield('leftJoyY', self.leftJoyY)
            yield('leftTrigger', self.leftTrigger)
            yield('rightTrigger', self.rightTrigger)
            yield ('centralButton', self.centralButton)

        except Exception as e:
            print(e)


class RemoteController:
    def __init__(self):
        self.first_pass = True
        self.arm_control_mode = False
        self.machine_control_mode = False
        self.motion_controller = MotionController()

    def loop(self):

        events = []
        manette = DictManette()

        while True:

            try:
                events = get_gamepad()
            except inputs.UnpluggedError:
                print("Pas de manette connectée")

            for event in events:

                if event.ev_type == "Key":  # Boutons A, B, X, Y, LB, RB

                    if event.code == "BTN_SOUTH":
                        manette.a = event.state

                        self.motion_controller.motion_control(manette)

                        # if event.state == pressed:
                        #     print "A pressed"
                        #     manette.a = event.state
                        #
                        #     self.send_message(Localhost, VizualizationModuleConstants,
                        #                       {'xbox_key': 'A_pressed'})
                        # elif event.state == released:
                        #     print "A released"
                        #     manette.a = event.state
                        #     self.send_message(Localhost, VizualizationModuleConstants,
                        #                       {'xbox_key': 'A_released'})

                    elif event.code == "BTN_NORTH":
                        manette.x = event.state
                        self.motion_controller.motion_control(manette)

                        # if event.state == pressed:
                        #     print "X pressed"
                        #     manette.x = event.state
                        #     self.send_message(Localhost, VizualizationModuleConstants,
                        #                       {'xbox_key': 'X_pressed'})
                        # elif event.state == released:
                        #     print("X released")
                        #     manette.x = event.state
                        #     self.send_message(Localhost, VizualizationModuleConstants,
                        #                       {'xbox_key': 'X_released'})

                    elif event.code == "BTN_EAST":
                        manette.b = event.state
                        self.motion_controller.motion_control(manette)

                        # if event.state == pressed:
                        #     print "B pressed"
                        #     manette.b = event.state
                        #     self.send_message(Localhost, VizualizationModuleConstants,
                        #                       {'xbox_key': 'B_pressed'})
                        # elif event.state == released:
                        #     print "B released"
                        #     manette.b = event.state
                        #     self.send_message(Localhost, VizualizationModuleConstants,
                        #                       {'xbox_key': 'B_released'})

                    elif event.code == "BTN_WEST":
                        manette.y = event.state
                        self.motion_controller.motion_control(manette)

                        # if event.state == pressed:
                        #     print "Y pressed"
                        #     manette.y = event.state
                        #     self.send_message(Localhost, VizualizationModuleConstants,
                        #                       {'xbox_key': 'Y_pressed'})
                        # elif event.state == released:
                        #     print "Y released"
                        #     manette.y = event.state
                        #     self.send_message(Localhost, VizualizationModuleConstants,
                        #                       {'xbox_key': 'Y_released'})

                    elif event.code == "BTN_MODE" and event.state == pressed:
                        manette.centralButton = pressed
                        self.motion_controller.motion_control(manette)
                        # self.send_message(Localhost, VizualizationModuleConstants, {'xbox_key': 'central_pressed'})

                    elif event.code == "BTN_TR":
                        manette.rb = event.state
                        self.motion_controller.motion_control(manette)

                        # if event.state == pressed:
                        #     manette.rb = event.state
                        #     self.send_message(Localhost, VizualizationModuleConstants,
                        #                       {'xbox_key': 'RB_pressed'})
                        # elif event.state == released:
                        #     manette.rb = event.state
                        #     self.send_message(Localhost, VizualizationModuleConstants,
                        #                       {'xbox_key': 'RB_released'})

                    elif event.code == "BTN_TL":
                        manette.lb = event.state
                        self.motion_controller.motion_control(manette)


                        # if event.state == pressed:
                        #     self.send_message(Localhost, VizualizationModuleConstants,
                        #                       {'xbox_key': 'LB_pressed'})
                        # elif event.state == released:
                        #     self.send_message(Localhost, VizualizationModuleConstants,
                        #                       {'xbox_key': 'LB_released'})

                elif event.ev_type == "Absolute":  # Triggers, pad et joysticks

                    # if event.code == "ABS_X":   # left joystick X
                    #     manette.leftJoyX = event.state
                    #     self.motion_controller.motion_control(manette)

                    if event.code == "ABS_Y":     # left joystick Y
                        manette.leftJoyY = -event.state
                        self.motion_controller.motion_control(manette)

                    # elif event.code == "ABS_RY":    # right joystick Y
                    #     manette.rightJoyY = event.state
                    #     self.motion_controller.motion_control(manette)

                    elif event.code == "ABS_RX":    # right joystick X
                        manette.rightJoyX = event.state
                        self.motion_controller.motion_control(manette)

                    elif event.code == "ABS_Z":  # Left trigger
                        #manette.leftTrigger = event.state
                        #self.send_message(list(LOCAL_HOST), ControlModuleConstants, {'xbox_ctrlr': dict(manette)})

                        if event.state == 255:
                            print("left trigger pressed")
                            self.arm_control_mode = True
                            manette.leftTrigger = 1

                            self.motion_controller.motion_control(manette)

                            # Utilisé pour la visualisation des commandes effectuées
                            # self.send_message(Localhost, VizualizationModuleConstants,
                            #                   {'xbox_key': 'LT_pressed'})

                        if event.state == 0:
                            self.arm_control_mode = False
                            manette.leftTrigger = 0

                            self.motion_controller.motion_control(manette)

                            # Utilisé pour la visualisation des commandes effectuées
                            # self.send_message(Localhost, VizualizationModuleConstants,
                            #                   {'xbox_key': 'LT_released'})

                    if event.code == "ABS_RZ":  # Right trigger
                        #manette.rightTrigger = event.state
                        #self.send_message(list(LOCAL_HOST), ControlModuleConstants, {'xbox_ctrlr': dict(manette)})


                        if event.state == 255:
                            self.machine_control_mode = True
                            manette.rightTrigger = 1
                            self.motion_controller.motion_control(manette)


                            # self.send_message(Localhost, VizualizationModuleConstants, {'xbox_key': 'RT_pressed'})

                        if event.state == 0:
                            self.machine_control_mode = False
                            manette.rightTrigger = 0
                            self.motion_controller.motion_control(manette)


                            # self.send_message(Localhost, VizualizationModuleConstants, {'xbox_key': 'RT_released'})

                    if event.code == "ABS_HAT0X":  # pad right et left

                        manette.padHorizontal = event.state
                        self.motion_controller.motion_control(manette)

                        # Pour la visualisation

                        # if event.state == 1:
                        #     self.send_message(Localhost, VizualizationModuleConstants, {'xbox_key': 'pad_right_pressed'})
                        #
                        # if event.state == -1:
                        #     self.send_message(Localhost, VizualizationModuleConstants, {'xbox_key': 'pad_left_pressed'})
                        #
                        # if event.state == 0:
                        #     self.send_message(Localhost, VizualizationModuleConstants, {'xbox_key': 'pad_hor_released'})

                    if event.code == "ABS_HAT0Y":  # pad up and down
                        manette.padVertical = event.state
                        self.motion_controller.motion_control(manette)

                        # Pour la visualisation

                        # if event.state == -1:
                        #     self.send_message(Localhost, VizualizationModuleConstants,
                        #                       {'xbox_key': 'pad_up_pressed'})
                        #
                        # if event.state == 1:
                        #     self.send_message(Localhost, VizualizationModuleConstants,
                        #                       {'xbox_key': 'pad_down_pressed'})
                        #
                        # if event.state == 0:
                        #     self.send_message(Localhost, VizualizationModuleConstants,
                        #                       {'xbox_key': 'pad_ver_released'})


def main():
    controller_module = RemoteController()
    controller_module.loop()


if __name__ == '__main__':
    main()
