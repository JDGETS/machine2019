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

# PUPPER BLACK
pupperblack_ip = '192.168.1.171'
pupperblack_motor_left_for_channel = 22
pupperblack_motor_left_back_channel = 26
pupperblack_motor_right_for_channel = 17
pupperblack_motor_right_back_channel = 27
pupperblack_light_channel = 5
pupperblack_servo_camera_channel = 13
pupperblack_for_speed = 84
pupperblack_start_speed = 28
pupperblack_back_speed = 49
pupperblack_rotation_speed = 49
pupperblack_acceleration_ratio = 7
pupperblack_servo_camera_front = 500
pupperblack_servo_camera_back = 2300
pupperblack_speed_motor_right = 100
pupperblack_speed_motor_left = 100
pupperblack_matrix_calibration_camera = [[2.589484213596329482e+03, 0, 1.698729966864577591e+03],[0., 2.598980566720857951e+03, 1.228227272486119546e+03], [0., 0., 1.]]
pupperblack_coefficient_distortion = [1.808684126195871100e-01,-4.092267392141504811e-01,7.927461711566604480e-03,1.114186232525689975e-03,2.145718416518574423e-01]

# PUPPER RED
pupperred_ip = '192.168.1.172'
pupperred_motor_left_for_channel = 22
pupperred_motor_left_back_channel = 26
pupperred_motor_right_for_channel = 27
pupperred_motor_right_back_channel = 17
pupperred_light_channel = 5
pupperred_servo_camera_channel = 13
pupperred_for_speed = 160
pupperred_back_speed = 100
pupperred_boost_speed = 230
pupperred_rotation_speed = 80
pupperred_acceleration_ratio = 20
pupperred_servo_camera_front = 620
pupperred_servo_camera_back = 2350
pupperred_speed_motor_right = 100
pupperred_speed_motor_left = 100
pupperred_matrix_calibration_camera = [[2.59970376e+03, 0, 1.66710857e+03],[0, 2.61837181e+03, 1.20139396e+03], [0., 0., 1.]]
pupperred_coefficient_distortion = [0.20709837, -0.51214243, 0.00323797, -0.00125799, 0.3661233]
