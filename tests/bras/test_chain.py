from dxl.dxlchain import DxlChain
import time

dyn_chain = DxlChain("/dev/ttyUSB0", rate=1000000)

print dyn_chain.get_motor_list()

print dyn_chain.get_position()

dyn_chain.close()
