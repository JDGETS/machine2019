import arm
import config
import os
import time
import ui

def main():
    stream_cmd = "i3-msg 'exec --no-startup-id mplayer -fps 200 -demuxer h264es ffmpeg://tcp://%s:9999'"

    # os.system(stream_cmd % config.doggo_arm_ip)
    # os.system(stream_cmd % config.doggo_overview_ip)

    time.sleep(1)

    os.system('''i3-msg '[class="MPlayer"] floating enable' ''')

    ui.main()
