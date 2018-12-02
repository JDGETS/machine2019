from arm import Arm
import rpyc
from rpyc.utils.server import ThreadedServer

ARM = Arm() # thread-safe instance

class ArmService(rpyc.Service):
    def exposed_goto(self, x, y, z, r, speed=50):
        ARM.goto(x, y, z, r, speed)



if __name__ == '__main__':
    ARM.open()

    RPC_PORT = 18861
    t = ThreadedServer(ArmService, port=RPC_PORT)
    t.start()
