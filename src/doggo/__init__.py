import arm
import config
import os
import time
import ui
from utils import wait_for_host

def main():
    print 'waiting for arm...'
    wait_for_host(config.doggo_arm_ip)

    print 'waiting for overview...'
    wait_for_host(config.doggo_overview_ip)

    print 'waiting for control...'
    wait_for_host(config.doggo_control_ip)

    stream_cmd = "i3-msg 'exec --no-startup-id mplayer -fps 200 -demuxer h264es ffmpeg://tcp://%s:9999' > /dev/null"

    print 'ready'
    print 'launching cameras...'

    if not os.getenv('NO_CAMERA'):
        os.system(stream_cmd % config.doggo_arm_ip)
        os.system(stream_cmd % config.doggo_overview_ip)
        
        time.sleep(1)

        os.system('''i3-msg '[class="MPlayer"] floating enable' ''')

    ui.main()
