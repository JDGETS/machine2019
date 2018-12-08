from dxl.dxlchain import DxlChain, DxlMotor
import time

chain = DxlChain("/dev/ttyUSB0", rate=1000000)

chain.open()


chain.motors[250] = DxlMotor.instantiateMotor(250, 12)

# chain.get_motor_list(broadcast=False)

motor_id = 250

chain.ping(motor_id)

chain.set_reg(250, 'max_torque', 1023)
chain.set_reg(250, 'torque_limit', 1023)

while True:
    load = chain.get_reg(250, 'present_load')
    direction = (load >> 10) & 1
    load = load & 1023

    speed = chain.get_reg(250, 'present_speed') & 1023


    print 'load = %d\tdir = %d\tspeed = %d' % (load, direction, speed)

    if load > 50:
        count += 1
    else:
        count = 0

    if count > 20:
        break


    chain.set_reg(250, 'moving_speed', 512)

    time.sleep(0.1)


chain.set_reg(250, 'moving_speed', 0)
chain.set_reg(250, 'torque_enable', 0)
