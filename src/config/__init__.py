import sys

def get_param(name):
    robot_type = sys.argv[1]

    return globals()[robot_type + '_' + name]



# DOGGO
doggo_control_ip = '192.168.0.160'
doggo_arm_ip = '192.168.0.161'
doggo_overview_ip = '192.168.0.162'

doggo_motor_left_for_channel = 13
doggo_motor_left_back_channel = 12
doggo_motor_right_for_channel = 27
doggo_motor_right_back_channel = 17

pupper_defaults = {

}

# PUPPER1
pupper1_ip =  '192.168.0.163'

# PUPPER2
pupper2_ip =  '192.168.0.164'