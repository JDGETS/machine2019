import ui
import os
import time
from utils import wait_for_host
from config import get_param


def main(instance):

    print 'waiting for connection to ' + instance + '...'
    wait_for_host(get_param('ip'))

    ui.main()
