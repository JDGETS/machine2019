from dxl.dxlchain import DxlChain, DxlMotor
import time

chain = DxlChain("/dev/ttyUSB0", rate=1000000)

chain.open()


# chain.motors[250] = DxlMotor.instantiateMotor(250, 12)

print chain.get_motor_list()

motor_id = 1

chain.ping(motor_id)


chain.set_reg(motor_id, 'cw_angle_limit', 0)
chain.set_reg(motor_id, 'ccw_angle_limit', 0)

chain.set_reg(motor_id, 'max_torque', 1023)
chain.set_reg(motor_id, 'torque_limit', 1023)

i = 0

while True:
    load = chain.get_reg(motor_id, 'present_load')
    direction = (load >> 10) & 1
    load = load & 1023

    speed = chain.get_reg(motor_id, 'present_speed') & 1023
    speed = (2 * direction - 1) * speed * 0.111
    temp =  chain.get_reg(motor_id, 'present_temp')


    print 'load = %d\tspeed = %d rpm\ttemp = %d' % (load, speed, temp)

    # wait 500 millis
    if i > 0.5 and abs(speed) <= 40:
        break

    chain.set_reg(motor_id, 'moving_speed', 512 + 1024)

    time.sleep(0.1)

    i += 0.1


chain.set_reg(motor_id, 'moving_speed', 0)
chain.set_reg(motor_id, 'torque_enable', 0)
