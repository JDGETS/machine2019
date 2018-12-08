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
    direction = load >> 10
    load = load % 1023

    print 'load = %d, dir = %d' % (load, direction)

    if load >= 9:
        chain.set_reg(250, 'moving_speed', 1023 + 1024)
        time.sleep(1)
        chain.set_reg(250, 'moving_speed', 0)
        time.sleep(0.2)

    time.sleep(0.1)
