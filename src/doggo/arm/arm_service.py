from arm import Arm
import rpyc
from rpyc.utils.server import ThreadedServer

ARM = Arm() # thread-safe instance

class ArmService(rpyc.Service):
    def _rpyc_getattr(self, name):
        # expose everything of the ARM instance
        return getattr(ARM, name)


def main():
    ARM.open()

    RPC_PORT = 18861
    t = ThreadedServer(ArmService, port=RPC_PORT)
    t.start()

if __name__ == '__main__':
    main()
