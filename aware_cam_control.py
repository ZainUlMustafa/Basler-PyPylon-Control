'''
AWARE CAM CONTROL [ACCON]
This is a specially designed camera booter that runs and auto tries to run camera
and fetch the required info. It is crash-safe which enables it to revive again and
again.

ACCON uses accon.json as strategy definer within which camera control properties can
be defined.
'''

import json
from operator import itemgetter
import os
import signal
from pypylon import pylon
import cv2
import numpy as np

showLogs = False
accon = './accon.json'
pid = None

def main():
    global pid; pid = os.getpid()

    if not os.path.exists(accon):
        print('ACCON config not found!')
        return
    #endif

    camIds = ["22730681"]
    cams = []

    while len(cams) == 0: 
        print("Waiting for camera...");
        cams = fetchCameras(camIds)
        print(cams)
    #endwhile

    converter = bgrConv()
    cam = cams[0]
    print(cam)
    cameraToPlay = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateDevice(cam))
    cameraToPlay.Open()
    cameraToPlay.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)
    print(f"{cam.GetSerialNumber()}: [Cameras opened]")

    while cameraToPlay.IsGrabbing():
        try:
            f = open(accon)
            data = json.load(f)
            f.close()

            camExposure, camGain, camLogs, camPid, camRetrievalTime, camShowImage, camKill = itemgetter('exposure', 'gain', 'showLogs', 'showPid', 'retrievalTime', 'showImage', 'kill')(data)
            
            if camPid:
                print(pid)
            #endif
            
            if camKill:
                os.kill(pid, signal.SIGTERM)
            #endif
            
            global showLogs; showLogs = camLogs
            buglog(data)

            cameraToPlay.ExposureTime.SetValue(camExposure)

            if (camGain <= 24.014275) and (camGain >= 0):
                cameraToPlay.Gain.SetValue(camGain)
            else:
                cameraToPlay.Gain.SetValue(0)
            #endif
        except Exception as e:
            print(e)
            buglog("Defaulted. Maybe incorrect ACCON data?")
        #endtry

        grabResult = cameraToPlay.RetrieveResult(camRetrievalTime, pylon.TimeoutHandling_ThrowException)
        if grabResult.GrabSucceeded():
            image = converter.Convert(grabResult)
            img = image.GetArray()

            if camShowImage:
                cv2.imshow('right', cv2.resize(img, (640*1,480*1)))

                if cv2.waitKey(1) & 0xff == ord('q'):
                    break
                #endif
            else:
                cv2.destroyAllWindows()
            #endif
        #endif

        grabResult.Release()
    #endwhile

    # Releasing the resource    
    cameraToPlay.StopGrabbing()
    cv2.destroyAllWindows()
#enddef

def buglog(data):
    if showLogs:
        print(f'[CAM LOGS]: {data}')
    #endif
#enddef

def fetchCameras(camIds):
    cams = []
    for camId in camIds:
        for cam in pylon.TlFactory.GetInstance().EnumerateDevices():
            if cam.GetSerialNumber() == camId:
                cams.append(cam)
            #endif
        #endfor
    #endfor

    return cams
#enddef

def bgrConv():
    converter = pylon.ImageFormatConverter()
    converter.OutputPixelFormat = pylon.PixelType_BGR8packed
    converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

    return converter
#enddef

if __name__ == "__main__":
    while True:
        try:
            cv2.destroyAllWindows()
            main()
        except:
            print("Reviving...")
        #endtry
    #endwhile
#endif

