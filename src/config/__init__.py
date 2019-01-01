import sys

def get_param(name):
    robot_type = sys.argv[1]

    return globals()[robot_type + '_' + name]


# DOGGO
doggo_control_ip = '192.168.1.160'
doggo_arm_ip = '192.168.1.161'
doggo_overview_ip = '192.168.1.162'

doggo_motor_left_for_channel = 13
doggo_motor_left_back_channel = 12
doggo_motor_right_for_channel = 27
doggo_motor_right_back_channel = 17
doggo_servo_arm_grip_channel = 22

pupper_defaults = {

}

# PUPPER1
pupper1_ip = '192.168.1.171'
pupper1_motor_left_for_channel = 22
pupper1_motor_left_back_channel = 26
pupper1_motor_right_for_channel = 17
pupper1_motor_right_back_channel = 27
pupper1_light_channel = 5
pupper1_servo_camera_channel = 13
pupper1_for_speed = 100
pupper1_back_speed = 50
pupper1_rotation_speed = 50
pupper1_acceleration_ratio = 5
pupper1_servo_camera_front = 500
pupper1_servo_camera_back = 2300
pupper1_speed_motor_right = 100
pupper1_speed_motor_left = 100
pupper1_matrix_calibration_camera = [[2.589484213596329482e+03, 0, 1.698729966864577591e+03],[0., 2.598980566720857951e+03, 1.228227272486119546e+03], [0., 0., 1.]]
pupper1_coefficient_distortion = [1.808684126195871100e-01,-4.092267392141504811e-01,7.927461711566604480e-03,1.114186232525689975e-03,2.145718416518574423e-01]

# PUPPER2
pupper2_ip = '192.168.1.172'
pupper2_motor_left_for_channel = 22
pupper2_motor_left_back_channel = 26
pupper2_motor_right_for_channel = 27
pupper2_motor_right_back_channel = 17
pupper2_light_channel = 5
pupper2_servo_camera_channel = 13
pupper2_for_speed = 160
pupper2_back_speed = 80
pupper2_rotation_speed = 40
pupper2_acceleration_ratio = 20
pupper2_servo_camera_front = 500
pupper2_servo_camera_back = 2300
pupper2_speed_motor_right = 100
pupper2_speed_motor_left = 100
pupper2_matrix_calibration_camera = [[2.589484213596329482e+03, 0, 1.698729966864577591e+03],[0., 2.598980566720857951e+03, 1.228227272486119546e+03], [0., 0., 1.]]
pupper2_coefficient_distortion = [1.808684126195871100e-01,-4.092267392141504811e-01,7.927461711566604480e-03,1.114186232525689975e-03,2.145718416518574423e-01]
