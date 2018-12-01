import rpyc
import sys
from rpyc.utils.server import ThreadedServer


# RPC service to have access to the arm remotely
class TestService(rpyc.Service):

    def on_connect(self, conn):
        # code that runs when a connection is created
        # (to init the service, if needed)
        pass

    def on_disconnect(self, conn):
        # code that runs after the connection has already closed
        # (to finalize the service, if needed)
        pass

    def exposed_get_question(self):  # while this method is not exposed
        return "what is the airspeed velocity of an unladen swallow?"

    def get_answer(self):
        return "youre not supposed to have access to this method remotely, its not exposed"


def server_side():
    t = ThreadedServer(TestService, port=18861)
    t.start()


def client_side():
    pi_hostname = 'raspberrypi-2'
    pi = rpyc.connect(pi_hostname, 18861)
    print pi.root.exposed_get_question()


if __name__ == "__main__":
    if sys.argv[1] == "client":
        client_side()
    elif sys.argv[1] == "server":
        server_side()
