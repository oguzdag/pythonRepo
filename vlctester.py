import vlc
import glob

import time
# https://is.gd/BpV1Fc.m3u8?EL_LINCE2021IPTV.m3u8
# http://iptvpro.watch-vision.net:8789/live/turk/ali/1096.ts




for filename in glob.glob('m3u\\*.m3u'):
    with open(filename) as f:
        print(filename)
        lines = f.read().splitlines()
        streambegin = False
        urlreceived = False
        for eachline in lines:
            if "EXTINF" in eachline:
                streambegin = True
                streaminfo = eachline
                continue
            if streambegin and ("http" in eachline):
                streamurl = eachline
                streambegin = False
                urlreceived = True

            if urlreceived and not streambegin:
                print(streaminfo)
                #print(streamurl)
                Instance = vlc.Instance('--novideo', '--run-time=5', '--quiet')
                player = Instance.media_player_new()
                Media = Instance.media_new(streamurl)
                Media.get_mrl()
                player.set_media(Media)
                player.play()
                time.sleep(1)
                validity = False
                while True:
                    state = str(player.get_state())
                    if state == "State.Ended":
                        validity = True
                        break
                    if state in ["State.Error","State.NothingSpecial"]:
                        validity = False
                        break
                    #print(str(state))
                    pass
                print(streamurl + " - " + str(validity))
                urlreceived = False
