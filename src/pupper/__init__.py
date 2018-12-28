import ui
import os
import time
from utils import wait_for_host
from config import get_param


def main(instance):

    print 'waiting for connection to ' + instance + '...'
    wait_for_host(get_param('ip'))

    stream_cmd = "mplayer -fps 200 -demuxer h264es ffmpeg://tcp://%s:9999 > /dev/null &"

    if not os.getenv('NO_CAMERA'):
        os.system(stream_cmd % get_param('_ip'))

        time.sleep(1)

        os.system('''i3-msg '[class="MPlayer"] floating enable' ''')

    ui.main()
