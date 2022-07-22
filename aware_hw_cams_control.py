import hashlib
import json
from operator import itemgetter
import os
import shutil
import signal
import time
from pypylon import pylon
import cv2
import numpy as np
import base64
import multiprocessing

production = False

configPath = "/Configurations"
dataPath = "/Data"

configDoc = configPath if production else '.' + '/configs/config.json'
settingDoc = configPath if production else '.' + '/configs/setting/ahccon.json'
statusDoc = configPath if production else '.' + '/configs/status/ahccon.json'

showLogs = False
pid = None
counter = 0
prevSetting = None
configData = None

def main():
    global pid; pid = os.getpid()
    camIds = ["22730681", "22730679"]
    cams = []

    cams = fetchCameras(camIds)
    converter = bgrConv()
    cam = cams[0]
    cameraToPlay = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateDevice(cam))
    cameraToPlay.Open()
    cameraToPlay.Gain.SetValue(0)
    cameraToPlay.TriggerSelector.SetValue("FrameStart")
    cameraToPlay.TriggerMode.SetValue("On")
    cameraToPlay.TriggerSource.SetValue('Line1')
    cameraToPlay.TriggerActivation.SetValue('RisingEdge')
    cameraToPlay.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

    print(cameraToPlay)

    grabbingCount = 0
    while cameraToPlay.IsGrabbing():
        try:
            startTime = time.time()
            grabResult = cameraToPlay.RetrieveResult(200, pylon.TimeoutHandling_ThrowException)
            if grabResult.GrabSucceeded():
                image = converter.Convert(grabResult)
                img = image.GetArray()

                cv2.imshow('right', cv2.resize(img, (640*1,480*1)))

                if cv2.waitKey(1) & 0xff == ord('q'):
                    os.kill(pid, signal.SIGTERM)
                    break
                #endif

                grabbingCount += 1
            #endif

            grabResult.Release()
            endTime = time.time()
            print(f"Total time taken this loop: {(endTime - startTime)*1000} ms")
        except:
            cv2.destroyAllWindows()
            print("Retrying...")
        #endtry
    #endwhile

    # Releasing the resource    
    cameraToPlay.StopGrabbing()
    cv2.destroyAllWindows()
#enddef

def fetchCameras(camIds: list):
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

def convertToB64(img):
    _, imArr = cv2.imencode('.png', img)  # imArr: image in Numpy one-dim array format.
    imBytes = imArr.tobytes()
    imB64 = base64.b64encode(imBytes)
    return imB64.decode("ascii")
#enddef

def currentServertime():
    return round(time.time() * 1000)
#enddef

def numberOfFiles(dir):
    list = os.listdir(dir)
    numberFiles = len(list)
    return numberFiles
#enddef

if __name__ == '__main__':
    cv2.destroyAllWindows()
    main()
#endif