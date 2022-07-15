'''
AWARE WEBCAM CONTROL [AWCON]
This is a specially designed camera booter that runs and auto tries to run camera
and fetch the required info. It is crash-safe which enables it to revive again and
again.

AWCON uses accon.json as strategy definer within which camera control properties can
be defined.
'''
print("ACCON INIT")
import json
from operator import itemgetter
import os
import signal
import cv2
import numpy as np

showLogs = False
awcon = './awcon.json'
pid = None
cap = None

def main():
    global pid; pid = os.getpid()

    if not os.path.exists(awcon):
        print('AWCON config not found!')
        return
    #endif

    while(cap.isOpened):
        try:
            f = open(awcon)
            data = json.load(f)
            f.close()

            cameraIndex, camLogs, camPid, camShowImage, camKill = itemgetter('cameraIndex', 'showLogs', 'showPid', 'showImage', 'kill')(data)
            
            if camPid:
                print(pid)
            #endif
            
            if camKill:
                cap.release()
                os.kill(pid, signal.SIGTERM)
            #endif
            
            global showLogs; showLogs = camLogs
            buglog(data)
        except Exception as e:
            print(e)
            buglog("Defaulted. Maybe incorrect AWCON data?")
        #endtry

        _, img = cap.read()

        if camShowImage:
            cv2.imshow('right', cv2.resize(img, (640*1,480*1)))

            if cv2.waitKey(1) & 0xff == ord('q'):
                break
            #endif
        else:
            cap.release()
            cv2.destroyAllWindows()
        #endif
    #endwhile

    cap.release()
    cv2.destroyAllWindows()
#enddef

def buglog(data):
    if showLogs:
        print(f'[CAM LOGS]: {data}')
    #endif
#enddef

if __name__ == '__main__':
    # main()
    count = 0
    while True:
        try:
            cv2.destroyAllWindows()
            print(f"CAP: {count}")
            cap = cv2.VideoCapture(count)
            main()
        except:
            if count < 10:
                count = count + 1
                cap.release()
                print(f"Reviving {count}...")
            else:
                count = 0
            #endif
        #endtry
    #endwhile
#endif