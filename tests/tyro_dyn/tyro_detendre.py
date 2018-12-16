from dxl.dxlchain import DxlChain, DxlMotor
import time

chain = DxlChain("/dev/ttyUSB0", rate=1000000)

chain.open()


# chain.motors[250] = DxlMotor.instantiateMotor(250, 12)

chain.get_motor_list()


motor_id = 1

chain.set_reg(motor_id, 'cw_angle_limit', 0)
chain.set_reg(motor_id, 'ccw_angle_limit', 0)

chain.ping(motor_id)

chain.set_reg(motor_id, 'max_torque', 1023)
chain.set_reg(motor_id, 'torque_limit', 1023)

while True:
    load = chain.get_reg(motor_id, 'present_load')
    direction = load >> 10
    load = load % 1023

    print 'load = %d, dir = %d' % (load, direction)

    if load >= 9:
        chain.set_reg(motor_id, 'moving_speed', 1023)
        time.sleep(1)
        chain.set_reg(motor_id, 'moving_speed', 0)
        time.sleep(0.2)

    time.sleep(0.1)
